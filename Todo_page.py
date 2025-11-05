import flet as ft
import datetime
import Todo_def  # 사용자 정의 모듈
import calendar
from flet import FilePickerResultEvent, padding
from dateutil import relativedelta
import traceback
import os 
import copy 
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError: 
    BASE_DIR = os.getcwd()
print(f"로그: 기준 경로는 {BASE_DIR} 입니다.")

JSON_FILE_PATH = os.path.join(BASE_DIR, "my_schedule.json")
print(f"로그: 저장 파일 경로는 {JSON_FILE_PATH} 입니다.")

def get_asset_path(file_name: str) -> str:
    return os.path.join(BASE_DIR, "assets", file_name)


def main(page: ft.Page):
    schedule_data = Todo_def.json_open(JSON_FILE_PATH)
    schedule_data = Todo_def.todo_import(schedule_data) 
    
    temp_items_by_id = {}
    for date_key, items_on_day in schedule_data.items():
        for item in items_on_day:
            item_id = (item.get('Title'), item.get('Start'))
            if item_id[0] and item_id[1]: 
                temp_items_by_id[item_id] = copy.deepcopy(item)
                
    all_items_data = list(temp_items_by_id.values()) 
    
    page.current_page = 1 
    ITEMS_PER_PAGE = 3
    page.editing_item_index = None 

    page.calendar_view_date = datetime.date.today()
    pre_to_day = datetime.date.today()
    page.filter_date = pre_to_day 

    # 1. "예" 버튼 클릭 시 (저장 후 종료)
    def yes_exit_click(e):
        print("로그: 사용자가 '예'를 선택했습니다. 데이터를 저장합니다...")
        try:
            Todo_def.json_save(schedule_data, JSON_FILE_PATH)
            print("로그: 데이터 저장 완료.")
        except Exception as ex:
            print(f"!!! 종료 중 저장 오류 발생: {ex}")
            traceback.print_exc()
        
        page.window.destroy()

    # 2. "아니오" 버튼 클릭 시 (다이얼로그만 닫기)
    def no_exit_click(e):
        page.close(exit_confirm_dialog)
        page.update()

    # 3. 종료 확인 다이얼로그 정의
    exit_confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("종료 확인"),
        content=ft.Text("정말로 앱을 종료하시겠습니까?"),
        actions=[
            ft.ElevatedButton("Yes", on_click=yes_exit_click),
            ft.OutlinedButton("No", on_click=no_exit_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.overlay.append(exit_confirm_dialog)

    # 4. 윈도우 이벤트 핸들러 (X 버튼 눌렀을 때)
    def window_event_handler(e: ft.ControlEvent):
        if e.data == "close":
            page.open(exit_confirm_dialog)
            page.update()

    # 5. Flet 페이지에 설정 적용
    page.window.prevent_close = True
    page.window.on_event = window_event_handler
    


    # --- (공통) 로케일 설정 ---
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("ko", "KR")],
        current_locale=ft.Locale("ko", "KR"),
    )

    # --- (공통) 사이드바 날짜 컨트롤 ---
    sidebar_month_text = ft.Text(
        value=pre_to_day.strftime("%m."), 
        size=20, weight=ft.FontWeight.W_500, color='#000000'
    )
    sidebar_day_text = ft.Text(
        value=pre_to_day.strftime("%d"), 
        size=25, weight=ft.FontWeight.W_500, color='#000000'
    )

    # --- 1. 기본 목록 뷰 (List View) ---
    todo_list = ft.Column(
        controls=[], scroll=ft.ScrollMode.AUTO, spacing=7,
        horizontal_alignment=ft.CrossAxisAlignment.START, expand=True
    )
    list_view_container = ft.Container(
        content=todo_list, 
        padding=ft.padding.all(20), 
        expand=True, 
        alignment=ft.alignment.top_left
    )

    # --- 2. 메모 뷰 (Memo View) ---
    memo_view_title = ft.Text(value="", size=18, weight=ft.FontWeight.BOLD, color="black")
    memo_view_duration = ft.Text(value="", size=18, color="black", weight=ft.FontWeight.BOLD) 
    memo_display_text = ft.Text(value="", size=14, selectable=True, color='black')
    memo_box_container = ft.Container(
        content=ft.Column(
            [memo_display_text], 
            scroll=ft.ScrollMode.AUTO,
            expand=True
        ),
        expand=True, 
        width=float('inf'),
        bgcolor='#F5F5F5',
        border=ft.border.all(1, '#E0E0E0'),
        border_radius=5,
        padding=10
    )
    back_to_list_button = ft.TextButton(
        "이전",
        width=60, height=30,
        tooltip="목록으로 돌아가기",
    )
    memo_view_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        memo_view_title,
                        ft.Container(expand=True), 
                        memo_view_duration 
                    ],
                    vertical_alignment="center"
                ),
                memo_box_container,
                ft.Row(
                    controls=[
                        ft.Container(expand=True), 
                        back_to_list_button
                    ]
                )
            ],
            expand=True 
        ),
        padding=ft.padding.all(20), 
        expand=True, 
        alignment=ft.alignment.top_left
    )
    
    # --- 3. 달력 뷰 (Calendar View) ---
    calendar_header_text = ft.Text(value="", size=15, weight=ft.FontWeight.BOLD, color="black")
    weekdays = ["일", "월", "화", "수", "목", "금", "토"]
    weekday_colors = ["red", "black", "black", "black", "black", "black", "blue"]
    calendar_weekday_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(weekdays[i], size=12, weight="bold", color=weekday_colors[i]),
                width=40, height=30, alignment=ft.alignment.center
            ) for i in range(7)
        ],
        spacing=0, alignment=ft.MainAxisAlignment.CENTER
    )
    calendar_days_container = ft.Column(
        controls=[], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    back_to_list_from_cal = ft.TextButton("이전", width=50, height=30, tooltip="목록으로 돌아가기")
    calendar_view_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            content=ft.Image(src=get_asset_path('Left.png'),width=15, height=15),
                            on_click=lambda e: change_month(e, -1)
                        ),
                        ft.Container(
                            content=calendar_header_text, 
                            alignment=ft.alignment.center
                        ),
                        ft.IconButton(
                            content=ft.Image(src=get_asset_path('Right.png'), width=15, height=15),
                            on_click=lambda e: change_month(e, 1)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=10
                ),
                calendar_weekday_row,
                calendar_days_container
            ],
            expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=20), 
        expand=True, 
        alignment=ft.alignment.top_center
    )
    
    # --- 4. 수정 항목 선택 뷰 (Edit Selection View) ---
    edit_selection_list = ft.Column(
        controls=[], scroll=ft.ScrollMode.AUTO, spacing=7,
        horizontal_alignment=ft.CrossAxisAlignment.START, expand=True
    )
    
    back_to_list_from_edit_select = ft.TextButton(
        "목록으로 돌아가기",
        height=30,
        on_click=lambda e: main_show_list(None), 
        style=ft.ButtonStyle(color="black") 
    )
    
    edit_selection_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("수정할 항목 선택", size=20, weight=ft.FontWeight.BOLD, color="black"),
                ft.Text(' ', size=12),
                edit_selection_list,
                ft.Row(
                    controls=[ft.Container(expand=True), back_to_list_from_edit_select],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            expand=True
        ),
        padding=ft.padding.all(20), 
        expand=True, 
        alignment=ft.alignment.top_left
    )
    
    # --- 5. 수정 폼 뷰 (Edit Form View) ---
    
    def edit_due_select_Day(e):
        selected_due_date = e.control.value
        edit_due_checkbox.data = selected_due_date 
        page.update()

    def edit_due_date_dismissal(e):
        edit_due_checkbox.value = False
        page.update()

    edit_due_picker = ft.DatePicker(
        on_change=edit_due_select_Day,
        on_dismiss=edit_due_date_dismissal
    )
    page.overlay.append(edit_due_picker) 

    # --- 삭제 로직: 'confirmed_delete' ---
    def confirmed_delete(e_dialog):
        nonlocal schedule_data
        nonlocal all_items_data
        page.close(delete_alert) 
        
        idx_to_delete = page.editing_item_index 
        filter_date_str = page.filter_date.isoformat()
        
        if idx_to_delete is None or idx_to_delete < 0:
            print(f"삭제 오류: 유효하지 않은 인덱스입니다. ({idx_to_delete})")
            main_show_list(None) 
            return
            
        try:
            deleted_item_instance = schedule_data[filter_date_str][idx_to_delete]
            item_id = (deleted_item_instance.get('Title'), deleted_item_instance.get('Start'))
            all_items_data = [
                item for item in all_items_data 
                if (item.get('Title'), item.get('Start')) != item_id
            ]
            print(f"항목 삭제 완료 (all_items_data): {item_id}")
            schedule_data = Todo_def.dict_end_edit(schedule_data, deleted_item_instance)
            print(f"항목 삭제 완료 (schedule_data): {item_id}")
            
        except (KeyError, IndexError) as e:
            print(f"삭제 중 오류 발생 (데이터 찾기 실패): {e}")
        except Exception as ex:
            print(f"삭제 중 알 수 없는 오류 발생: {ex}")
        
        page.editing_item_index = None
        update_ui_display()
        main_show_list(None)
    
    def cancel_delete(e_dialog):
        page.close(delete_alert)

    delete_alert = ft.AlertDialog(
        modal=True,
        title=ft.Text("항목 삭제"),
        content=ft.Text("이 항목을 정말로 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다."),
        actions=[
            ft.TextButton("취소", on_click=cancel_delete),
            ft.TextButton(
                "삭제", 
                on_click=confirmed_delete,
                style=ft.ButtonStyle(color="red")
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def delete_item_click(e):
        page.open(delete_alert)

    page.overlay.append(delete_alert)

    def edit_due_picker_set(e):
        if e.control.value: 
            start_date = edit_start_text.data 
            if start_date:
                edit_due_picker.first_date = start_date
                edit_due_picker.value = start_date
                page.open(edit_due_picker)
            else:
                pass 
        else: 
            edit_due_checkbox.data = None
            page.update()

    edit_title = ft.Text(value='일정 수정', size=20, weight=ft.FontWeight.BOLD, color="black")
    edit_delete_button = ft.TextButton(
        '삭제', height=30,
        on_click=delete_item_click,
        style=ft.ButtonStyle(color='red')
        )
    edit_todo_field = ft.TextField(label="Title", width=250) 
    
    edit_start_text = ft.Text(
        value="시작일: (불러오는 중)", data=None, 
        weight=ft.FontWeight.BOLD, color="black"
    )
    edit_due_checkbox = ft.Checkbox(
        label='마감일 설정', on_change=edit_due_picker_set, data=None,
        label_style=ft.TextStyle(color="black") 
    )
    
    edit_memo_checkbox = ft.Checkbox(
        label='메모 추가', 
        on_change=lambda e: setattr(edit_memo_field, 'visible', e.control.value) or page.update(),
        label_style=ft.TextStyle(color="black") 
    )
    edit_memo_field = ft.TextField(label='memo', width=250, visible=False)
    
    edit_link_checkbox = ft.Checkbox(
        label='링크 추가', 
        on_change=lambda e: setattr(edit_link_field, 'visible', e.control.value) or page.update(),
        label_style=ft.TextStyle(color="black") 
    )
    edit_link_field = ft.TextField(label='link', width=250, visible=False)
    
    edit_nextDay = ft.Checkbox(
        label='미완료 시 다음 일정에 자동 적용',
        label_style=ft.TextStyle(color="black") 
    )

    # '수정 저장' 버튼 로직
    def save_edit_button_click(e):
        nonlocal schedule_data
        nonlocal all_items_data
        
        idx = page.editing_item_index 
        filter_date_str = page.filter_date.isoformat()

        if idx is None or idx < 0:
            print("오류: 수정할 항목 인덱스가 잘못되었습니다.")
            main_show_list(None)
            return

        if not edit_todo_field.value:
            print("경고: 제목을 입력해주세요.")
            return

        try:
            original_data = schedule_data[filter_date_str][idx]
        except (KeyError, IndexError, TypeError):
            print(f"오류: 수정할 원본 데이터를 찾을 수 없습니다. ({filter_date_str}[{idx}])")
            main_show_list(None)
            return

        new_title = edit_todo_field.value
        new_start_str = edit_start_text.data.strftime('%Y-%m-%d') # 'Start'는 변경 불가
        new_memo = edit_memo_field.value if edit_memo_checkbox.value else None
        new_link = edit_link_field.value if edit_link_checkbox.value else None
        new_due_val = edit_due_checkbox.data.strftime('%Y-%m-%d') if edit_due_checkbox.value and edit_due_checkbox.data else None
        new_nextday = edit_nextDay.value
        
        original_due_str = original_data.get('Due')

        if original_due_str != new_due_val:
            print("로그: 마감일이 변경되어 글로벌 수정을 수행합니다.")
            
            # (A) 새 데이터 객체 생성
            updated_data = {
                'Title': new_title,
                'Start': new_start_str,
                'Memo': new_memo,
                'Link': new_link,
                'Due': new_due_val,
                'NextDay': new_nextday,
                'Status': original_data.get('Status', 0) # Status는 현재 값 유지
            }
            
            # (B) schedule_data에서 모든 기존 항목 삭제
            schedule_data = Todo_def.dict_end_edit(schedule_data, original_data)
            
            # (C) schedule_data에 새 항목으로 재등록
            new_save_format = { updated_data['Start']: updated_data }
            schedule_data = Todo_def.dict_add(new_save_format, schedule_data)
            
            # (D) all_items_data에서도 마스터 항목 교체
            item_id = (original_data['Title'], original_data['Start'])
            for i, item in enumerate(all_items_data):
                if (item.get('Title'), item.get('Start')) == item_id:
                    all_items_data[i] = copy.deepcopy(updated_data) 
                    break
            print(f"항목 {item_id}가 'all_items_data' 리스트(UI용)에서 수정되었습니다.")

        else:
            # --- [2] 로컬 수정 로직 (신규 방식: 마감일 변경 없음) ---
            print(f"로그: {filter_date_str}의 항목을 로컬 수정합니다.")
            
            # (A) schedule_data의 해당 날짜 항목만 직접 수정
            target_item = schedule_data[filter_date_str][idx]
            target_item['Title'] = new_title
            target_item['Memo'] = new_memo
            target_item['Link'] = new_link
            target_item['NextDay'] = new_nextday
            # Status, Start, Due는 변경되지 않음
            
            print(f"항목 {filter_date_str}[{idx}]가 'schedule_data'에서 수정되었습니다.")

        page.editing_item_index = None
        update_ui_display()
        main_show_list(None)

    save_edit_button = ft.TextButton('저장', on_click=save_edit_button_click)
    
    cancel_edit_button = ft.TextButton(
        "취소", 
        on_click=lambda e: main_show_list(None),
        style=ft.ButtonStyle(color="black") 
    )

    edit_form_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[edit_title, ft.Container(expand=True),edit_delete_button, ft.Text(' ')], alignment=ft.MainAxisAlignment.CENTER), 
                edit_todo_field, edit_start_text, edit_due_checkbox,
                edit_memo_checkbox, edit_memo_field,
                edit_link_checkbox, edit_link_field, edit_nextDay,
                ft.Row(
                    controls=[ft.Container(expand=True), cancel_edit_button, save_edit_button],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START
        ),
        padding=ft.padding.all(20),
        expand=True
    )

    ### --- 6. 파일 템플릿 불러오기 뷰 ---
    def add_file_start_Day(e):
        selected_date_obj = e.control.value.date()
        
        print(f"선택된 날짜: {selected_date_obj.strftime('%Y-%m-%d')}")
        file_start_button.data = selected_date_obj 
        page.update()
        
    def add_file_start_dismissal(e):
        print("DatePicker가 닫혔습니다.")
        file_start_button.value = False
        page.update()

    add_file_start_picker = ft.DatePicker(
        on_change=add_file_start_Day,
        first_date=datetime.date.today(),
        on_dismiss=add_file_start_dismissal
    )
    page.overlay.append(add_file_start_picker)

    def open_add_file_start_picker(e):
        if e.control.value:
            page.open(add_file_start_picker)
        else:
            e.control.data = None
            page.update()
    
    file_path_text = ft.Text(value="", size=14, color="black", weight=ft.FontWeight.BOLD, data=None)
    file_start_button = ft.Checkbox(label='시작일 설정', on_change=open_add_file_start_picker, data=None, label_style=ft.TextStyle(color="black"))
    
    # --- '파일 저장' 버튼 로직 (dict_import) ---
    def file_start_save(e):
        nonlocal schedule_data
        nonlocal all_items_data
        
        template_path = file_path_text.data
        start_day_obj = file_start_button.data
        
        if not template_path:
            print("오류: 불러올 JSON 파일이 선택되지 않았습니다.")
            return
            
        try:
            template_data = Todo_def.json_open(template_path)
            if not template_data:
                print(f"오류: 템플릿 파일({template_path})이 비어있거나 손상되었습니다.")
                return

            start_day_str = None
            date_to_filter_to = None

            if start_day_obj:
                # 사용자가 날짜를 선택한 경우
                start_day_str = start_day_obj.isoformat()
                date_to_filter_to = start_day_obj
            else:
                # 사용자가 날짜를 선택 안 한 경우 (템플릿 원본 날짜 사용)
                try:
                    min_key_str = min(template_data.keys()) 
                    date_to_filter_to = datetime.date.fromisoformat(min_key_str)
                except (ValueError, TypeError, AttributeError):
                    date_to_filter_to = datetime.date.today() # 비상시 오늘 날짜
            

            
            schedule_data = Todo_def.dict_import(
                template_data, 
                start_day=start_day_str, 
                existing=schedule_data
            )
            
            # UI용 all_items_data 리스트 전면 재구성
            temp_items_by_id = {}
            for date_key, items_on_day in schedule_data.items():
                for item in items_on_day:
                    item_id = (item.get('Title'), item.get('Start'))
                    if item_id[0] and item_id[1]:
                        temp_items_by_id[item_id] = copy.deepcopy(item)
            all_items_data = list(temp_items_by_id.values())
            
            print(f"로그: {template_path}에서 템플릿을 성공적으로 불러왔습니다.")
            if date_to_filter_to:
                page.filter_date = date_to_filter_to
                sidebar_month_text.value = page.filter_date.strftime("%m.")
                sidebar_day_text.value = page.filter_date.strftime("%d")
                page.current_page = 1

            update_ui_display() # 새 'filter_date'로 UI를 갱신
            main_show_list(None)
            
        except Exception as ex:
            print(f"파일 불러오기 중 심각한 오류 발생: {ex}")
            traceback.print_exc()
    
    def file_start_cancel(e): 
        file_start_button.data = None
        file_path_text.data = None
        show_add_form_view(None)
    
    file_save_button = ft.TextButton('저장', on_click=file_start_save)
    file_cancel_button = ft.TextButton(
        '취소',
        on_click=file_start_cancel,
        style=ft.ButtonStyle(color="black")
    )
    
    file_start_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("파일 시작일 설정", size=20, weight=ft.FontWeight.BOLD, color="black"),
                ft.Container(height=20),
                file_path_text,
                ft.Container(height=5),
                file_start_button,
                ft.Container(expand=True),
                ft.Row(
                    controls=[ft.Container(expand=True), file_cancel_button, file_save_button],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START
        ),
        padding=ft.padding.all(20),
        expand=True
    )

    # --- 7. 일정 추가 폼 뷰 (Add Form View) ---
    def on_dialog_result(e: FilePickerResultEvent):
        if e.files:
            selected_file_path = e.files[0].path
            print(f"선택한 파일 경로: {selected_file_path}")
            
            file_path_text.value = f"선택된 파일: {selected_file_path}"
            file_path_text.data = selected_file_path
            file_start_button.data = None
            
            pagination_row.visible = False
            main_switch.content = file_start_container
            main_switch.update()
            page.update()
        else:
            print("파일 선택이 취소되었습니다.")
        page.update()

    def add_start_select_Day(e):
        selected_date_obj = e.control.value.date()
        
        print(f"선택된 날짜: {selected_date_obj.strftime('%Y-%m-%d')}")
        add_start_button.data = selected_date_obj
        add_start_button.text = selected_date_obj.strftime('%Y-%m-%d')
        page.update()

    def add_start_date_dismissal(e):
        print("DatePicker가 닫혔습니다.")
        page.update()
        
    add_start_date_picker = ft.DatePicker(
        on_change=add_start_select_Day,
        first_date=datetime.date.today(),
        on_dismiss=add_start_date_dismissal
    )
    
    def add_due_select_Day(e):
        selected_due_date = e.control.value
        print(f"선택된 날짜: {selected_due_date.strftime('%Y-%m-%d')}")
        add_due_checkbox.data = selected_due_date
        page.update()

    def add_due_date_dismissal(e):
        print("DatePicker가 닫혔습니다.")
        add_due_checkbox.value = False
        page.update()
        print("날짜가 선택되지 않아 마감 체크를 해제합니다.")

    add_due_picker = ft.DatePicker(
        on_change=add_due_select_Day,
        on_dismiss=add_due_date_dismissal
    )
    
    page.overlay.append(add_start_date_picker)
    page.overlay.append(add_due_picker)
    
    def add_start_picker_set(e):
        page.open(add_start_date_picker)
        
    def add_memo_change(e):
        add_memo_field.visible = e.control.value
        page.update()

    def add_link_change(e):
        add_link_field.visible = e.control.value
        page.update()
        
    def add_due_picker_set(e):
        def not_have_start(e_dialog):
            page.close(start_alert)
            add_due_checkbox.value = False
            page.update()
        
        if e.control.value:
            if add_start_button.data:
                add_due_picker.first_date = add_start_button.data
                add_due_picker.value = add_start_button.data
                page.open(add_due_picker)
            else:
                start_alert = ft.AlertDialog(
                    modal=True, title=ft.Text("경고"),
                    content=ft.Text("시작일을 선택해주세요."),
                    actions=[ft.TextButton("확인", on_click=not_have_start)],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(start_alert)
                return
        else:
            add_due_checkbox.data = None
            page.update()
    
    def reset_add_form():
        add_todo_field.value = ""
        add_start_button.text = "시작일 설정"
        add_start_button.data = None
        add_due_checkbox.value = False
        add_due_checkbox.data = None
        add_memo_checkbox.value = False
        add_memo_field.value = ""
        add_memo_field.visible = False
        add_link_checkbox.value = False
        add_link_field.value = ""
        add_link_field.visible = False
        add_nextDay_checkbox.value = False
    
    # --- '일정 저장' 버튼 로직 (dict_add) ---
    def add_save_data(e):
        nonlocal schedule_data
        
        if not add_todo_field.value:
            title_alert = ft.AlertDialog(
                modal=True, title=ft.Text("경고"),
                content=ft.Text("제목(Title)을 입력해주세요."),
                actions=[ft.TextButton("확인", on_click=lambda e: page.close(title_alert))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(title_alert)
            return
        
        ko_bid_cnt = 0
        lit_int_cnt = 0
        for i in add_todo_field.value:
            if i.islower() or i.isdigit():
                lit_int_cnt += 1
            elif i.isupper() or 'ㄱ' <= i <= 'ㅎ' or 'ㅏ' <= i <= 'ㅣ' or '가' <= i <= '힣':
                ko_bid_cnt += 1
            else:
                lit_int_cnt += 1
            
        if (lit_int_cnt//2)+ko_bid_cnt > 20 :
            len_title_alert = ft.AlertDialog(
                modal=True, title=ft.Text("경고"),
                content=ft.Text("제목(Title)의 내용을 줄여주세요."),
                actions=[ft.TextButton("확인", on_click=lambda e: page.close(len_title_alert))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(len_title_alert)
            return
            
        if not add_start_button.data:
            start_alert = ft.AlertDialog(
                modal=True, title=ft.Text("경고"),
                content=ft.Text("시작일을 선택해주세요."),
                actions=[ft.TextButton("확인", on_click=lambda e: page.close(start_alert))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(start_alert)
            return

        def M_reset(e_dialog):
            add_memo_checkbox.value = False
            add_memo_field.visible = False
            page.close(memo_alert)
            page.update()
        def L_reset(e_dialog):
            add_link_checkbox.value = False
            add_link_field.visible = False
            page.close(link_alert)
            page.update()

        if add_memo_checkbox.value and not add_memo_field.value:
            memo_alert = ft.AlertDialog(
                modal=True, title=ft.Text("경고"),
                content=ft.Text("메모(Memo)를 입력해주세요."),
                actions=[
                    ft.TextButton("확인", on_click=lambda e: page.close(memo_alert)),
                    ft.TextButton("취소", on_click=M_reset)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(memo_alert)
            return
        if add_link_checkbox.value and not add_link_field.value:
            link_alert = ft.AlertDialog(
                modal=True, title=ft.Text("경고"),
                content=ft.Text("링크(Link)를 입력해주세요."),
                actions=[
                    ft.TextButton("확인", on_click=lambda e: page.close(link_alert)),
                    ft.TextButton("취소", on_click=L_reset)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(link_alert)
            return

        startVal = add_start_button.data.strftime('%Y-%m-%d') if add_start_button.data else None
        dueVal = add_due_checkbox.data.strftime('%Y-%m-%d') if add_due_checkbox.value and add_due_checkbox.data else None

        check_save_data = {
            'Title': add_todo_field.value,
            'Start': startVal,
            'Memo': add_memo_field.value if add_memo_checkbox.value else None,
            'Link': add_link_field.value if add_link_checkbox.value else None,
            'Due': dueVal,
            'NextDay': add_nextDay_checkbox.value,
            'Status': 0
        }
        print("--- 저장 시작 ---")
        print(check_save_data)

        new_save_format = { startVal: check_save_data }
        schedule_data = Todo_def.dict_add(new_save_format, schedule_data)
        print("항목이 'schedule_data' 딕셔너리(저장용)에 추가되었습니다.")

        all_items_data.append(check_save_data)
        print("항목이 'all_items_data' 리스트(UI용)에 추가되었습니다.")
        
        reset_add_form() 
        
        page.filter_date = datetime.datetime.strptime(startVal, '%Y-%m-%d').date()
        sidebar_month_text.value = page.filter_date.strftime("%m.")
        sidebar_day_text.value = page.filter_date.strftime("%d")
        page.current_page = 1 
        
        update_ui_display()
        main_show_list(None)

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    add_file_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(name="upload_file", size=14, color="#3E6D91"), 
                ft.Text("파일 선택", size=12, color="#3E6D91") 
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        border=ft.border.all(1, "#E0E0E0"),
        border_radius=0,
        padding=padding.symmetric(horizontal=8, vertical=4),
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["json"]
        ),
        tooltip="JSON 파일 선택"
    )
    
    add_title = ft.Text(value='일정 추가', size=20, weight=ft.FontWeight.BOLD, color="black")
    add_todo_field = ft.TextField(label="Title", width=250)
    add_start_button = ft.TextButton('시작일 설정', on_click=add_start_picker_set, data=None)
    add_due_checkbox = ft.Checkbox(label='마감일 설정', on_change=add_due_picker_set, data=None, label_style=ft.TextStyle(color="black"))
    add_memo_checkbox = ft.Checkbox(label='메모 추가', on_change=add_memo_change, label_style=ft.TextStyle(color="black"))
    add_memo_field = ft.TextField(label='memo', width=250, visible=False)
    add_link_checkbox = ft.Checkbox(label='링크 추가', on_change=add_link_change, label_style=ft.TextStyle(color="black"))
    add_link_field = ft.TextField(label='link', width=250, visible=False)
    add_nextDay_checkbox = ft.Checkbox(label='미완료 시 다음 일정에 자동 적용', label_style=ft.TextStyle(color="black"))
    add_save_button = ft.TextButton('적용', on_click=add_save_data)
    add_cancel_button = ft.TextButton(
        "취소", 
        on_click=lambda e: main_show_list(None) or reset_add_form(),
        style=ft.ButtonStyle(color="black")
    )

    add_form_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[add_title, add_file_button], spacing=70), add_todo_field, add_start_button, add_due_checkbox,
                add_memo_checkbox, add_memo_field,
                add_link_checkbox, add_link_field, add_nextDay_checkbox,
                ft.Row(
                    controls=[ft.Container(expand=True), add_cancel_button, add_save_button],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START
        ),
        padding=ft.padding.all(20),
        expand=True
    )
    
    # === 뷰 전환 메인 스위치 ===
    main_switch = ft.AnimatedSwitcher(
        content=list_view_container,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
        reverse_duration=200,
        expand=True
    )

    pageBtn_L = ft.IconButton(
        content=ft.Image(src='Left.png', width=15, height=15),
        tooltip='Left', width=25, height=25,
    )
    pageNum = ft.Text(value='1/1', size=10, weight=ft.FontWeight.W_500, color='black')
    pageBtn_R = ft.IconButton(
        content=ft.Image(src='Right.png', width=15, height=15),
        tooltip='Right', width=25, height=25,
    )

    pagination_row = ft.Row(
        controls=[pageBtn_L, pageNum, pageBtn_R],
        alignment=ft.MainAxisAlignment.CENTER, spacing=5,
        visible=True
    )
    
    # === 뷰 전환 및 핸들러 함수 ===
    def main_show_list(e):
        page.window.height = 365
        main_switch.content = list_view_container
        page.editing_item_index = None
        pagination_row.visible = True
        main_switch.update()
        page.update()
    
    def show_add_form_view(e):
        page.window.height = 365
        pagination_row.visible = False
        reset_add_form()
        main_switch.content = add_form_container
        main_switch.update()
        page.update()

    back_to_list_button.on_click = main_show_list
    back_to_list_from_cal.on_click = main_show_list

    # 캘린더 UI 생성 함수
    def build_calendar_ui():
        calendar.setfirstweekday(calendar.SUNDAY)
        year = page.calendar_view_date.year
        month = page.calendar_view_date.month
        calendar_header_text.value = f"{year}년 {month}월"
        calendar_days_container.controls.clear()
        
        today = datetime.date.today()
        selected_date = page.filter_date
        
        events_on_day = {}
        for date_str, items_list in schedule_data.items():
            try:
                current_day = datetime.date.fromisoformat(date_str)
                if current_day.year == year and current_day.month == month and items_list:
                    events_on_day[current_day.day] = True
            except (ValueError, TypeError):
                continue
        
        month_matrix = calendar.monthcalendar(year, month)
        for week in month_matrix:
            week_row_controls = []
            for day_idx, day in enumerate(week):
                if day == 0:
                    week_row_controls.append(ft.Container(width=40, height=38))
                else:
                    current_day_date = datetime.date(year, month, day) 
                    is_today = (current_day_date == today) 
                    is_selected = (current_day_date == selected_date)
                    
                    text_color = "red" if day_idx == 0 else ("blue" if day_idx == 6 else "black")
                    bgcolor = "transparent"
                    border = None
                    text_weight = "normal"
                    
                    if is_today and not is_selected:
                        bgcolor = "transparent"
                        border = ft.border.all(1, "#3E91E4")
                        text_color = "#3E91E4"
                        text_weight = "bold"
                    
                    if is_selected:
                        bgcolor = "#1976D2"
                        border = None
                        text_color = "white"
                        text_weight = "bold"

                    day_content = ft.Container(
                        content=ft.Text(value=str(day), size=12, weight=text_weight, color=text_color),
                        alignment=ft.alignment.center, width=30, height=30,
                        bgcolor=bgcolor, border=border, border_radius=15,
                    )
                    
                    has_event = events_on_day.get(day, False)
                    event_dot = ft.Container(
                        width=5, height=5, bgcolor="red" if has_event else "transparent",
                        border_radius=2.5, margin=ft.margin.only(top=1)
                    )
                    day_stack = ft.Column(
                        controls=[day_content, event_dot],
                        spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER, height=38
                    )
                    week_row_controls.append(
                        ft.Container(
                            content=day_stack, alignment=ft.alignment.top_center, 
                            width=40, height=38,
                            on_click=lambda e, d=day: on_calendar_day_click(d), ink=True
                        )
                    )
            calendar_days_container.controls.append(
                ft.Row(controls=week_row_controls, spacing=0, alignment=ft.MainAxisAlignment.CENTER)
            )
        if main_switch.content == calendar_view_container:
            page.update()

    # 달력 날짜 클릭 핸들러
    def on_calendar_day_click(day):
        selected_date = page.calendar_view_date.replace(day=day)
        page.filter_date = selected_date
        sidebar_month_text.value = selected_date.strftime("%m.")
        sidebar_day_text.value = selected_date.strftime("%d")
        page.current_page = 1
        update_ui_display()
        main_show_list(None)

    # 달력 월 변경 핸들러
    def change_month(e, delta):
        current_date = page.calendar_view_date
        new_date = current_date + relativedelta(months=delta)
        page.calendar_view_date = new_date.replace(day=1)
        build_calendar_ui()
        page.update()

    # 캘린더 뷰 표시
    def show_calendar_view(e):
        page.window.height = 385
        pagination_row.visible = False
        page.calendar_view_date = page.filter_date.replace(day=1)
        build_calendar_ui() 
        main_switch.content = calendar_view_container
        main_switch.update()
        page.update()

    # 메모 뷰 기간 계산
    def calculate_duration(reference_date, due_date_str):
        if not due_date_str:
            return "" 
        try:
            start_date = reference_date 
            due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
            delta = (due_date - start_date).days
            
            if delta < 0:
                return f"(D+{-delta}일)"
            elif delta == 0:
                return "(D-Day)"
            else:
                return f"(D-{delta}일)"
        except (ValueError, TypeError) as e:
            print(f"calculate_duration 오류: {e}")
            return ""

    # 메모 뷰 표시
    def main_clean(e, item_data):
        memo_text = item_data.get('Memo')
        title_text = item_data.get('Title')
        due_val = item_data.get('Due')
        
        memo_view_title.value = title_text
        memo_view_duration.value = calculate_duration(page.filter_date, due_val)
        
        memo_display_text.value = memo_text if memo_text else "저장된 메모가 없습니다."
        pagination_row.visible = False
        main_switch.content = memo_view_container
        main_switch.update()

    

    # 수정 폼 채우기
    def start_editing_item(item_index_in_day):
        page.editing_item_index = item_index_in_day # '그날 리스트'의 인덱스
        filter_date_str = page.filter_date.isoformat()

        try:
            item_data = schedule_data[filter_date_str][item_index_in_day]
        except (KeyError, IndexError) as e:
            print(f"오류: 항목 인덱스 {item_index_in_day}를 schedule_data['{filter_date_str}']에서 찾을 수 없습니다. {e}")
            main_show_list(None)
            return
            
        edit_todo_field.value = item_data.get('Title')
        
        start_str = item_data.get('Start')
        start_date_obj = datetime.datetime.strptime(start_str, '%Y-%m-%d').date()
        edit_start_text.value = f"시작일: {start_str} (변경 불가)"
        edit_start_text.data = start_date_obj 
        
        due_str = item_data.get('Due')
        if due_str:
            edit_due_checkbox.value = True
            edit_due_checkbox.data = datetime.datetime.strptime(due_str, '%Y-%m-%d').date()
        else:
            edit_due_checkbox.value = False
            edit_due_checkbox.data = None
            
        memo_val = item_data.get('Memo')
        edit_memo_checkbox.value = bool(memo_val)
        edit_memo_field.value = memo_val if memo_val else ""
        edit_memo_field.visible = bool(memo_val)

        link_val = item_data.get('Link')
        edit_link_checkbox.value = bool(link_val)
        edit_link_field.value = link_val if link_val else ""
        edit_link_field.visible = bool(link_val)

        edit_nextDay.value = item_data.get('NextDay', False)

        pagination_row.visible = False
        
        main_switch.content = edit_form_container
        page.update()

    # 수정 항목 선택 뷰 표시
    def show_edit_selection_view(e):
        page.window.height = 365
        pagination_row.visible = True
        edit_selection_list.controls.clear()
        filter_date_str = page.filter_date.isoformat()
        items_on_day = schedule_data.get(filter_date_str, [])
        
        total_items = len(items_on_day)
        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
        if total_items == 0: total_pages = 1
        if page.current_page > total_pages: page.current_page = total_pages
        
        start_index = (page.current_page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        
        tuples_to_display = items_on_day[start_index:end_index]
        pageNum.value = f"{page.current_page}/{total_pages}" 

        if not tuples_to_display:
            edit_selection_list.controls.append(ft.Text("수정할 항목이 없습니다.", color="black"))
        else:
            for i, item in enumerate(tuples_to_display):
                actual_idx_in_day = start_index + i 
                
                edit_selection_list.controls.append(
                    ft.Checkbox(
                        label=f" {item.get('Title')}", 
                        value=False,
                        data=actual_idx_in_day,
                        label_style=ft.TextStyle(color="black", size= 14),
                        on_change=lambda e, idx=actual_idx_in_day: start_editing_item(idx) if e.control.value else None 
                    )
                )
                edit_selection_list.controls.append(ft.Text(' ', style=ft.TextStyle(size= 10)))

        main_switch.content = edit_selection_container
        main_switch.update()
        page.update()

    # --- UI 갱신 함수 (메인 리스트) ---
    def update_ui_display():
        try:
            todo_list.controls.clear()
            filter_date_str = page.filter_date.isoformat()
            items_on_day = schedule_data.get(filter_date_str, [])

            total_items = len(items_on_day)
            total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
            if total_items == 0: total_pages = 1 
            if page.current_page > total_pages: page.current_page = total_pages
            start_index = (page.current_page - 1) * ITEMS_PER_PAGE
            end_index = start_index + ITEMS_PER_PAGE
            
            tuples_to_display = items_on_day[start_index:end_index]
            pageNum.value = f"{page.current_page}/{total_pages}"

            for i, item in enumerate(tuples_to_display):
                actual_idx_in_day = start_index + i

                title_text = item.get('Title', '')
                start_val = item.get('Start', None)
                due_val = item.get('Due', None)
                memo_val = item.get('Memo')
                link_val = item.get('Link')
                status = item.get('Status', 0)
                
                pre_link = {}
                if link_val:
                    try:
                        pre_link = Todo_def.url_mention(link_val)
                    except Exception as e:
                        print(f"url_mention 오류: {e}")
                        pre_link = {'title': '링크 처리 중 오류', 'favicon_url': None, 'url': link_val}
                
                status_map = { 0: "▢", 1: "O", 2: "△", 3: "X" }
                status_display = status_map.get(status, "▢")

                status_text_control = ft.Text(
                    value=status_display, 
                    size=16, 
                    weight="w500", 
                    color="black"
                )
                
                # Status 변경 핸들러
                def create_status_handler(date_key, item_index_in_day, dic_value, text_control_to_update):
                    def on_status_select(e):
                        nonlocal schedule_data
                        try:
                            schedule_data[date_key][item_index_in_day]['Status'] = dic_value
                            
                            print(f"로컬 상태 변경: {date_key}[{item_index_in_day}]의 상태를 {dic_value}(으)로 변경")
                            
                            text_control_to_update.value = status_map.get(dic_value, "▢")
                            page.update()
                            
                        except KeyError:
                            print(f"Status 변경 오류: 잘못된 날짜 키 {date_key}")
                        except IndexError:
                            print(f"Status 변경 오류: 잘못된 인덱스 {item_index_in_day}")
                        except Exception as ex:
                            print(f"Status 변경 중 심각한 오류: {ex}")
                            traceback.print_exc()
                            
                    return on_status_select

                status_popup = ft.PopupMenuButton(
                    content=status_text_control, 
                    items=[
                        ft.PopupMenuItem(text="O", on_click=create_status_handler(filter_date_str, actual_idx_in_day, 1, status_text_control)),
                        ft.PopupMenuItem(text="△", on_click=create_status_handler(filter_date_str, actual_idx_in_day, 2, status_text_control)),
                        ft.PopupMenuItem(text="X", on_click=create_status_handler(filter_date_str, actual_idx_in_day, 3, status_text_control)),
                    ], 
                    tooltip='complete'
                )
                
                memo_button = ft.IconButton(
                    content=ft.Image(src=get_asset_path('memo.png'), width=12, height=12),
                    opacity=1.0 if memo_val else 0.0,
                    tooltip="메모 보기",
                    on_click=lambda e, item_ref=item: main_clean(e, item_ref),
                    width=30, height=30
                )
                title_row = ft.Row(
                    controls=[
                        status_popup,
                        ft.Text(value=title_text, size=16, weight="w500", color="black"),
                        ft.Container(expand=True), memo_button
                    ], vertical_alignment="center", spacing=5
                )
                
                dday_text = calculate_duration(page.filter_date, due_val)

                due_text_control = ft.Text(
                    value=f"Due: {due_val} {dday_text}" if due_val else " ", 
                    size=11, color="black", 
                    opacity=1.0 if due_val else 0.0 
                )
                
                link_controls_list = []
                actual_url = pre_link.get('url')
                click_handler = (lambda _, url=actual_url: page.launch_url(url) if url else None)
                tooltip_text = f"링크 열기: {actual_url}" if actual_url else None

                if link_val: 
                    favicon_url = pre_link.get('favicon_url')
                    link_title = pre_link.get('title')

                    if favicon_url:
                        link_controls_list.append(
                            ft.Image(src=favicon_url, width = 15, height = 15)
                        )
                        link_controls_list.append(
                            ft.Text(link_title, size=12, weight=ft.FontWeight.W_500, color="black")
                        )
                    elif actual_url:
                        link_controls_list.append(
                            ft.Text(
                                actual_url, size=12, weight=ft.FontWeight.W_500, 
                                color="blue", italic=True
                            )
                        )

                icon_row_contents = ft.Row(
                    controls=link_controls_list, 
                    spacing=5,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
                
                icon_row_controls = ft.Container(
                    content=icon_row_contents,
                    on_click=click_handler, 
                    tooltip=tooltip_text,
                    padding=0,
                    height=16,
                    opacity=1.0 if link_val else 0.0,
                )
                
                new_item_controls = [title_row, due_text_control, icon_row_controls]
                new_item = ft.Container(
                    content=ft.Column(controls=new_item_controls, spacing=1, tight=True),
                    padding=ft.padding.only(left=10, top=12, right=10, bottom=12),
                    bgcolor='#F5F5F5', border_radius=5, border=ft.border.all(1, '#E0E0E0')
                )
                todo_list.controls.append(new_item)

            page.update() 
            
            if main_switch.content != list_view_container:
                print("다른 뷰(메모/달력)가 활성 중이므로, 목록 UI는 백그라운드에서 갱신됨.")
            print(f"UI 업데이트 완료. 현재 {page.current_page}/{total_pages} 페이지 표시 (필터링된 항목 기준).")

        except Exception as e:
            print(f"!!!!!!!! update_ui_display 함수 전체에서 치명적인 오류 발생: {e} !!!!!!!!")
            traceback.print_exc()
            todo_list.controls.clear()
            todo_list.controls.append(ft.Text(f"오류: {e}", color="red"))
            page.update()

    # --- 페이징 핸들러 (뷰 상태 인지) ---
    def on_page_left(e):
        if page.current_page > 1:
            page.current_page -= 1
            if main_switch.content == edit_selection_container:
                show_edit_selection_view(None)
            else:
                update_ui_display() 

    def on_page_right(e):
        filter_date_str = page.filter_date.isoformat()
        items_on_day = schedule_data.get(filter_date_str, [])
        total_items = len(items_on_day)

        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
        if total_items == 0: total_pages = 1
            
        if page.current_page < total_pages:
            page.current_page += 1
            if main_switch.content == edit_selection_container:
                show_edit_selection_view(None)
            else:
                update_ui_display()
                
    pageBtn_L.on_click = on_page_left
    pageBtn_R.on_click = on_page_right
    page.title = 'Py-Scheduler'
    page.window.width = 585
    page.window.height = 365
    page.window.resizable = False
    page.window.maximizable = False
    page.padding = 0
    page.bgcolor = '#FFFFFF'
    
    sidebar = ft.Container(
        width=90, height=450, bgcolor='#D9D9D9',
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                sidebar_month_text, 
                sidebar_day_text,  
                ft.Container(height=20),
                ft.IconButton(
                    content=ft.Image(src='Add.png', width=25, height=25), 
                    on_click=show_add_form_view, 
                    tooltip='add'
                ),
                ft.Container(height=15),
                ft.IconButton(
                    content=ft.Image(src='Canlender.png', width=25, height=25), 
                    tooltip='calender',
                    on_click=show_calendar_view 
                ),
                ft.Container(height=15),
                ft.IconButton(
                    content=ft.Image(src='edit.png', width=20, height=20), 
                    tooltip='edit',
                    on_click=show_edit_selection_view 
                ),
                ft.Container(expand=True),
                pagination_row,
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0
        )
    )

    layout = ft.Row(controls=[sidebar, main_switch], spacing=0, expand=True)
    page.add(layout)
    
    # --- 초기 UI 로드 ---
    update_ui_display()

# --- 앱 실행 ---
if __name__ == "__main__":
    ft.app(target=main)