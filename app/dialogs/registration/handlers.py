"""Обработчики для диалога регистрации на мероприятия."""
from typing import Any

from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button, Select

from app.services.event_service import EventService
from app.services.user_service import UserService
from app.states import RegistrationSG, MainMenuSG


async def on_enter_events_list(
    callback,
    result,
    dialog_manager: DialogManager
):
    """Обработчик входа в список мероприятий."""
    # Предзаполняем данные текущими регистрациями
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    
    telegram_id = callback.from_user.id if callback else dialog_manager.event.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if user:
        registrations = await event_service.get_user_registrations(user.id)
        selected_events = [str(reg.event.id) for reg in registrations]
        dialog_manager.dialog_data["selected_optional"] = selected_events
        print(f"DEBUG: Preloaded selections: {selected_events}")


async def on_toggle_event_registration(
    callback,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
    **kwargs
):
    """Обработчик переключения выбора мероприятия (только в состоянии диалога)."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    
    try:
        event_id = int(item_id)
        event = await event_service.get_event_by_id(event_id)
        
        if not event:
            await callback.message.answer("❌ Мероприятие не найдено.")
            return
        
        # Получаем текущий выбор из состояния диалога
        current_selections = dialog_manager.dialog_data.get("selected_optional", [])
        
        # Переключаем выбор
        if item_id in current_selections:
            # Убираем из выбора
            current_selections.remove(item_id)
        else:
            # Добавляем в выбор
            # Для взаимоисключающих мероприятий убираем другие взаимоисключающие
            if event.is_exclusive:
                # Убираем другие взаимоисключающие мероприятия из выбора
                all_events = await event_service.get_all_events()
                for other_event in all_events:
                    if other_event.is_exclusive and other_event.id != event_id:
                        other_id_str = str(other_event.id)
                        if other_id_str in current_selections:
                            current_selections.remove(other_id_str)
                            await callback.message.answer(f"➖ Автоматически убрано (конфликт времени): {other_event.name}")
            
            current_selections.append(item_id)
        
        # Сохраняем обновленный выбор в состоянии диалога
        dialog_manager.dialog_data["selected_optional"] = current_selections
        
        print(f"DEBUG: Updated selections: {current_selections}")
        
    except ValueError:
        await callback.message.answer("❌ Ошибка: некорректный ID мероприятия.")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")


async def on_confirm_final_registration(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик подтверждения изменений - реальное сохранение в БД и Google Sheets."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    telegram_id = callback.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if not user:
        await callback.message.answer("❌ Сначала необходимо пройти регистрацию.")
        return
    
    # Получаем желаемый выбор из состояния диалога
    desired_selections = dialog_manager.dialog_data.get("selected_optional", [])
    
    # Получаем текущие регистрации из БД
    current_registrations = await event_service.get_user_registrations(user.id)
    current_ids = [str(reg.event.id) for reg in current_registrations]
    
    # Определяем, что нужно добавить и что убрать
    to_register = [event_id for event_id in desired_selections if event_id not in current_ids]
    to_unregister = [event_id for event_id in current_ids if event_id not in desired_selections]
    
    success_count = 0
    error_messages = []
    
    try:
        # Сначала проверяем лимиты для новых регистраций
        for event_id_str in to_register:
            event_id = int(event_id_str)
            event = await event_service.get_event_by_id(event_id)
            if not event:
                error_messages.append(f"Мероприятие с ID {event_id} не найдено")
                continue
                
            # Проверяем лимиты
            registered_count = await event_service.get_registered_count(event_id)
            if event.max_participants and registered_count >= event.max_participants:
                error_messages.append(f"🔒 Мероприятие '{event.name}' заполнено (лимит: {event.max_participants})")
        
        # Если есть ошибки с лимитами, не продолжаем
        if error_messages:
            error_text = "❌ Не удалось сохранить изменения:\n" + "\n".join(error_messages)
            await callback.message.answer(error_text)
            await dialog_manager.switch_to(RegistrationSG.optional_events, show_mode=ShowMode.DELETE_AND_SEND)
            return
        
        # Отменяем ненужные регистрации
        for event_id_str in to_unregister:
            event_id = int(event_id_str)
            success, message = await event_service.unregister_user_from_event(user, event_id)
            if success:
                success_count += 1
            else:
                error_messages.append(f"Ошибка отмены: {message}")
        
        # Добавляем новые регистрации
        for event_id_str in to_register:
            event_id = int(event_id_str)
            success, message = await event_service.register_user_for_event(user, event_id)
            if success:
                success_count += 1
            else:
                error_messages.append(f"Ошибка регистрации: {message}")
        
        # Формируем итоговое сообщение
        if success_count > 0:
            result_message = f"✅ Изменения успешно сохранены! Обработано операций: {success_count}"
            if error_messages:
                result_message += f"\n\n⚠️ Ошибки:\n" + "\n".join(error_messages)
        elif error_messages:
            result_message = "❌ Не удалось сохранить изменения:\n" + "\n".join(error_messages)
        else:
            result_message = "ℹ️ Нет изменений для сохранения"
        
        await callback.message.answer(result_message)
        await dialog_manager.switch_to(RegistrationSG.my_registrations, show_mode=ShowMode.DELETE_AND_SEND)
        
    except Exception as e:
        await callback.message.answer(f"❌ Критическая ошибка при сохранении: {str(e)}")
        await dialog_manager.switch_to(RegistrationSG.optional_events, show_mode=ShowMode.DELETE_AND_SEND)


async def on_edit_registrations(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик перехода к управлению регистрациями."""
    await dialog_manager.switch_to(RegistrationSG.optional_events, show_mode=ShowMode.DELETE_AND_SEND)


async def on_unregister_event(
    callback,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
    **kwargs
):
    """Обработчик отмены регистрации на мероприятие."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    telegram_id = callback.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if not user:
        await callback.message.answer("❌ Пользователь не найден.")
        return
    
    try:
        event_id = int(item_id)
        success, message = await event_service.unregister_user_from_event(user, event_id)
        
        if success:
            await callback.message.answer(f"✅ {message}")
        else:
            await callback.message.answer(f"❌ {message}")
            
    except ValueError:
        await callback.message.answer("❌ Ошибка: некорректный ID мероприятия.")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при отмене регистрации: {str(e)}")


async def on_back_to_menu(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик возврата в главное меню."""
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.start(MainMenuSG.menu, mode=StartMode.RESET_STACK)