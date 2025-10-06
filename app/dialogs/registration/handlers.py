"""Обработчики для диалога регистрации на мероприятия."""
from typing import Any

from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button, Select, ManagedRadio, ManagedCheckbox

from app.services.event_service import EventService
from app.services.user_service import UserService
from app.states import RegistrationSG, MainMenuSG


async def on_exclusive_event_changed(
    callback,
    radio: ManagedRadio,
    dialog_manager: DialogManager,
    item_id: str,
    **kwargs
):
    """Обработчик изменения выбора взаимоисключающего мероприятия."""
    # Сохраняем выбор в состоянии диалога
    dialog_manager.dialog_data["selected_exclusive"] = item_id


async def on_optional_event_changed(
    callback,
    checkbox: ManagedCheckbox,
    dialog_manager: DialogManager,
    **kwargs
):
    """Обработчик изменения выбора дополнительного мероприятия."""
    # Получаем текущие выборы дополнительных мероприятий
    current_selections = dialog_manager.dialog_data.get("selected_optional", [])
    
    # Получаем все чекбоксы и их состояния
    selected_optional = []
    
    # Проходим по всем дополнительным мероприятиям и проверяем их состояние
    dialog_data = dialog_manager.dialog_data
    
    # Сохраняем обновленный список в состоянии
    dialog_manager.dialog_data["selected_optional"] = selected_optional


async def on_skip_exclusive(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик пропуска взаимоисключающих мероприятий."""
    # Очищаем выбор взаимоисключающих мероприятий
    dialog_manager.dialog_data["selected_exclusive"] = None
    # Переходим к дополнительным мероприятиям
    await dialog_manager.next()


async def on_enter_optional_events(
    callback,
    result,
    dialog_manager: DialogManager
):
    """Обработчик входа в окно дополнительных мероприятий."""
    # Предзаполняем чекбоксы при входе в окно
    try:
        from .getters import get_optional_events_data
        optional_data = await get_optional_events_data(dialog_manager)
        
        plenary_checked = optional_data.get("plenary_checked", False)
        vtb_checked = optional_data.get("vtb_checked", False)
        
        print(f"DEBUG: Setting checkboxes - plenary: {plenary_checked}, vtb: {vtb_checked}")
        
        # Устанавливаем чекбоксы
        plenary_checkbox = dialog_manager.find("plenary_checkbox")
        if plenary_checkbox:
            await plenary_checkbox.set_checked(plenary_checked)
        
        vtb_checkbox = dialog_manager.find("vtb_checkbox")
        if vtb_checkbox:
            await vtb_checkbox.set_checked(vtb_checked)
    except Exception as e:
        print(f"DEBUG: Error setting checkboxes: {e}")


async def on_next_to_optional(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик перехода к дополнительным мероприятиям."""
    await dialog_manager.next()


async def on_next_to_confirmation(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик перехода к подтверждению."""
    # Собираем выбранные чекбоксы
    selected_optional = []
    
    # Получаем данные о дополнительных мероприятиях для определения ID
    from .getters import get_optional_events_data
    optional_data = await get_optional_events_data(dialog_manager)
    
    # Находим события по их sheet_name
    plenary_event_id = None
    vtb_event_id = None
    
    for event in optional_data["optional_events"]:
        if event.sheet_name == "plenary_session":
            plenary_event_id = str(event.id)
        elif event.sheet_name == "vtb_speech":
            vtb_event_id = str(event.id)
    
    # Проверяем состояние чекбоксов
    try:
        plenary_checkbox = dialog_manager.find("plenary_checkbox")
        if plenary_checkbox and plenary_checkbox.is_checked() and plenary_event_id:
            selected_optional.append(plenary_event_id)
    except:
        pass
    
    try:
        vtb_checkbox = dialog_manager.find("vtb_checkbox")
        if vtb_checkbox and vtb_checkbox.is_checked() and vtb_event_id:
            selected_optional.append(vtb_event_id)
    except:
        pass
    
    # ВАЖНО: Сохраняем выбранные дополнительные мероприятия
    dialog_manager.dialog_data["selected_optional"] = selected_optional
    
    # Логируем для отладки
    print(f"DEBUG: selected_optional = {selected_optional}")
    print(f"DEBUG: dialog_data = {dialog_manager.dialog_data}")
    
    await dialog_manager.next()


async def on_confirm_final_registration(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик финального подтверждения регистрации."""
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    
    telegram_id = callback.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if not user:
        await callback.message.answer("❌ Сначала необходимо пройти регистрацию.")
        return
    
    # Получаем выбранные мероприятия
    selected_exclusive = dialog_manager.dialog_data.get("selected_exclusive")
    selected_optional = dialog_manager.dialog_data.get("selected_optional", [])
    
    all_selected = []
    if selected_exclusive:
        all_selected.append(selected_exclusive)
    all_selected.extend(selected_optional)
    
    if not all_selected:
        await callback.message.answer("❌ Необходимо выбрать хотя бы одно мероприятие.")
        return
    
    # Сначала отменяем все текущие регистрации
    current_registrations = await event_service.get_user_registrations(user.id)
    for reg in current_registrations:
        await event_service.unregister_user_from_event(user, reg.event.id)
    
    # Регистрируем на выбранные мероприятия
    success_count = 0
    error_messages = []
    
    for event_id_str in all_selected:
        try:
            event_id = int(event_id_str)
            success, message = await event_service.register_user_for_event(user, event_id)
            if success:
                success_count += 1
            else:
                error_messages.append(message)
        except ValueError:
            error_messages.append(f"Некорректный ID мероприятия: {event_id_str}")
    
    # Формируем итоговое сообщение
    if success_count > 0:
        result_message = f"✅ Успешно зарегистрированы на {success_count} мероприятий!"
        if error_messages:
            result_message += f"\n\n⚠️ Ошибки:\n" + "\n".join(error_messages)
    else:
        result_message = "❌ Регистрация не удалась:\n" + "\n".join(error_messages)
    
    await callback.message.answer(result_message)
    
    # Переходим к просмотру регистраций
    await dialog_manager.switch_to(RegistrationSG.my_registrations)


async def on_edit_registrations(callback, button: Button, dialog_manager: DialogManager):
    """Обработчик изменения регистраций."""
    # Предзаполняем данные текущими регистрациями
    user_service: UserService = dialog_manager.middleware_data["user_service"]
    event_service: EventService = dialog_manager.middleware_data["event_service"]
    
    telegram_id = callback.from_user.id
    user = await user_service.get_user_by_telegram_id(telegram_id)
    
    if user:
        registrations = await event_service.get_user_registrations(user.id)
        
        # Предзаполняем состояние диалога
        selected_exclusive = None
        selected_optional = []
        
        for reg in registrations:
            if reg.event.is_exclusive:
                selected_exclusive = str(reg.event.id)
            else:
                selected_optional.append(str(reg.event.id))
        
        dialog_manager.dialog_data["selected_exclusive"] = selected_exclusive
        dialog_manager.dialog_data["selected_optional"] = selected_optional
        
        # Устанавливаем состояние Radio для взаимоисключающих мероприятий
        if selected_exclusive:
            dialog_manager.dialog_data["exclusive_radio_state"] = selected_exclusive
        
        # Устанавливаем состояние чекбоксов
        dialog_manager.dialog_data["plenary_checked"] = False
        dialog_manager.dialog_data["vtb_checked"] = False
        
        # Получаем данные о мероприятиях для определения чекбоксов
        all_events = await event_service.get_all_events()
        for event in all_events:
            if str(event.id) in selected_optional:
                if event.sheet_name == "plenary_session":
                    dialog_manager.dialog_data["plenary_checked"] = True
                elif event.sheet_name == "vtb_speech":
                    dialog_manager.dialog_data["vtb_checked"] = True
    
    # Начинаем заново с взаимоисключающих мероприятий
    await dialog_manager.switch_to(RegistrationSG.exclusive_events)


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