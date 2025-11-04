import flet as ft
import multiprocessing
import datetime
import threading
import time
import queue 
import Todo_def
import calendar
from dateutil.relativedelta import relativedelta

def add_window(page: ft.Page, queue_from_main: multiprocessing.Queue):
    
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("ko", "KR")],
        current_locale=ft.Locale("ko", "KR"),
    )

    def start_select_Day(e):
        page.selected_date = e.control.value
        print(f"선택된 날짜: {page.selected_date.strftime('%Y-%m-%d')}")
        start.data = page.selected_date
        start.text = page.selected_date.strftime('%Y-%m-%d')
        page.update()

    def start_date_dismissal(e):
        print("DatePicker가 닫혔습니다.")
        page.update()
        
    start_date_picker = ft.DatePicker(
        on_change=start_select_Day,
        first_date=datetime.date.today(),
        on_dismiss=start_date_dismissal
    )
    
    page.overlay.append(start_date_picker)
    
    def start_picker_set(e):
        page.open(start_date_picker)
        
    def memo_change(e):
        memo_field.visible = e.control.value
        page.update()

    def link_change(e):
        link_field.visible = e.control.value
        page.update()
        
    def due_select_Day(e):
        selected_due_date = e.control.value
        print(f"선택된 날짜: {selected_due_date.strftime('%Y-%m-%d')}")
        due.data = selected_due_date
        page.update()

    def due_date_dismissal(e):
        print("DatePicker가 닫혔습니다.")
        due.value = False
        page.update()
        print("날짜가 선택되지 않아 마감 체크를 해제합니다.")

    due_picker = ft.DatePicker(
        on_change=due_select_Day,
        on_dismiss=due_date_dismissal
    )
    page.overlay.append(due_picker)

    def due_picker_set(e):
        def not_have_start(e):
            page.close(start_alert)
            due.value = False
            page.update()
        
        if e.control.value:
            if start.data:
                due_picker.first_date = start.data
                due_picker.value = start.data
                page.open(due_picker)
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
            due.data = None
            page.update()
    
    def save_data(e):
        if not todo_field.value:
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
        for i in todo_field.value:
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
            
        if not start.data:
            start_alert = ft.AlertDialog(
                modal=True, title=ft.Text("경고"),
                content=ft.Text("시작일을 선택해주세요."),
                actions=[ft.TextButton("확인", on_click=lambda e: page.close(start_alert))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(start_alert)
            return

        def M_reset(e):
            memo.value = False
            memo_field.visible = False
            page.close(memo_alert)
            page.update()
        def L_reset(e):
            link.value = False
            link_field.visible = False
            page.close(link_alert)
            page.update()
        if memo.value and not memo_field.value:
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
        if link.value and not link_field.value:
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

        startVal = start.data.strftime('%Y-%m-%d') if start.data else None
        dueVal = due.data.strftime('%Y-%m-%d') if due.value and due.data else None

        check_save_data = {
            'Title': todo_field.value,
            'Start': startVal,
            'Memo': memo_field.value if memo.value else None,
            'Link': link_field.value if link.value else None,
            'Due': dueVal,
            'NextDay': nextDay.value,
            'Status': None
        }
        print("--- 저장 시작 ---")
        print(check_save_data)

        if queue_from_main:
            queue_from_main.put(check_save_data)
            print("Queue에 데이터 전달 완료!")
        else:
            print("오류: Queue가 전달되지 않았습니다.")

        page.window.destroy()

    page.title = "Add 윈도우"
    page.window.width = 585
    page.window.height = 365
    page.window.resizable = False
    page.window.maximizable = False

    title = ft.Text(value='일정 추가', size=20, weight=ft.FontWeight.BOLD)
    todo_field = ft.TextField(label="Title", width=250)
    start = ft.TextButton('시작일 설정', on_click=start_picker_set, data=None)
    due = ft.Checkbox(label='마감일 설정', on_change=due_picker_set)
    memo = ft.Checkbox(label='메모 추가', on_change=memo_change)
    memo_field = ft.TextField(label='memo', width=250, visible=False)
    link = ft.Checkbox(label='링크 추가', on_change=link_change)
    link_field = ft.TextField(label='link', width=250, visible=False)
    nextDay = ft.Checkbox(label='미완료 시 다음 일정에 자동 적용')
    save_btn = ft.ElevatedButton(text='Save', on_click=save_data)

    scrollable_column = ft.Column(
        controls=[
            title, todo_field, start, due, memo, memo_field,
            link, link_field, nextDay, save_btn
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.START
    )
    page.add(scrollable_column)

def start_add_window_app(child_queue: multiprocessing.Queue):
    ft.app(target=lambda p: add_window(p, child_queue))

def main(page: ft.Page, main_queue: multiprocessing.Queue):
    
    all_items_data = [] 
    page.current_page = 1 
    ITEMS_PER_PAGE = 3
    page.editing_item_index = None # ★ (수정) 수정 기능용 인덱스

    page.calendar_view_date = datetime.date.today()
    pre_to_day = datetime.date.today()
    page.filter_date = pre_to_day # ★ (달력) 필터 날짜 상태

    # ★ (달력) 사이드바 날짜 컨트롤을 변수로
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
    
    # --- 3. ★ (달력) 달력 뷰 (Calendar View) ---
    calendar_header_text = ft.Text(value="", size=18, weight="bold", color="black")
    weekdays = ["일", "월", "화", "수", "목", "금", "토"]
    weekday_colors = ["red", "black", "black", "black", "black", "black", "blue"]
    calendar_weekday_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(weekdays[i], size=12, weight="bold", color=weekday_colors[i]),
                width=40, height=25, alignment=ft.alignment.center
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
                            content=ft.Icon(name="ARROW_BACK_IOS", size=20),
                            on_click=lambda e: change_month(e, -1)
                        ),
                        ft.Container(
                            content=calendar_header_text, 
                            alignment=ft.alignment.center, 
                            expand=True
                        ),
                        ft.IconButton(
                            content=ft.Icon(name="ARROW_FORWARD_IOS", size=20),
                            on_click=lambda e: change_month(e, 1)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=10
                ),
                ft.Container(height=10),
                calendar_weekday_row,
                ft.Container(height=5),
                calendar_days_container,
                ft.Row(controls=[ft.Container(expand=True), back_to_list_from_cal])
            ],
            expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=20), 
        expand=True, 
        alignment=ft.alignment.top_center
    )
    
    # --- 4. ★ (수정) 수정 항목 선택 뷰 (Edit Selection View) ---
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
    
    # --- 5. ★ (수정) 수정 폼 뷰 (Edit Form View) ---
    
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
    
    save_edit_button = ft.ElevatedButton(text='저장')
    
    cancel_edit_button = ft.TextButton(
        "취소", 
        on_click=lambda e: main_show_list(None),
        style=ft.ButtonStyle(color="black") 
    )

    edit_form_container = ft.Container(
        content=ft.Column(
            controls=[
                edit_title, edit_todo_field, edit_start_text, edit_due_checkbox,
                edit_memo_checkbox, edit_memo_field,
                edit_link_checkbox, edit_link_field, edit_nextDay,
                ft.Row(controls=[ft.Container(expand=True), cancel_edit_button, save_edit_button])
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
    
    # === 뷰 전환 및 핸들러 함수 ===
    
    def main_show_list(e):
        main_switch.content = list_view_container
        page.editing_item_index = None
        main_switch.update()
    
    back_to_list_button.on_click = main_show_list
    back_to_list_from_cal.on_click = main_show_list

    # ★ (달력) 캘린더 UI 생성 함수 (이벤트 점 포함)
    def build_calendar_ui():
        calendar.setfirstweekday(calendar.SUNDAY)
        year = page.calendar_view_date.year
        month = page.calendar_view_date.month
        calendar_header_text.value = f"{year}년 {month}월"
        calendar_days_container.controls.clear()
        
        events_on_day = {}
        for item in all_items_data:
            item_start_str = item.get('Start')
            if not item_start_str: continue
            try:
                item_start_date = datetime.datetime.strptime(item_start_str, '%Y-%m-%d').date()
                item_due_str = item.get('Due')
                if item_due_str:
                    item_due_date = datetime.datetime.strptime(item_due_str, '%Y-%m-%d').date()
                    current_day = item_start_date
                    while current_day <= item_due_date:
                        if current_day.year == year and current_day.month == month:
                            if current_day.day not in events_on_day:
                                events_on_day[current_day.day] = True
                        if current_day.year > year or (current_day.year == year and current_day.month > month):
                             break
                        current_day += datetime.timedelta(days=1)
                else:
                    if item_start_date.year == year and item_start_date.month == month:
                         if item_start_date.day not in events_on_day:
                            events_on_day[item_start_date.day] = True
            except ValueError:
                continue
        
        month_matrix = calendar.monthcalendar(year, month)
        for week in month_matrix:
            week_row_controls = []
            for day_idx, day in enumerate(week):
                if day == 0:
                    week_row_controls.append(ft.Container(width=40, height=38))
                else:
                    is_today = (day == datetime.date.today().day and month == datetime.date.today().month and year == datetime.date.today().year)
                    text_color = "white" if is_today else ("red" if day_idx == 0 else ("blue" if day_idx == 6 else "black"))
                    
                    day_content = ft.Container(
                        content=ft.Text(value=str(day), size=12, weight="bold" if is_today else "normal", color=text_color),
                        alignment=ft.alignment.center, width=30, height=30,
                        bgcolor="#1976D2" if is_today else None, border_radius=15,
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

    # ★ (달력) 달력 날짜 클릭 핸들러
    def on_calendar_day_click(day):
        selected_date = page.calendar_view_date.replace(day=day)
        page.filter_date = selected_date
        sidebar_month_text.value = selected_date.strftime("%m.")
        sidebar_day_text.value = selected_date.strftime("%d")
        page.current_page = 1
        update_ui_display()
        main_show_list(None)

    # ★ (달력) 달력 월 변경 핸들러
    def change_month(e, delta):
        current_date = page.calendar_view_date
        new_date = current_date + relativedelta(months=delta)
        page.calendar_view_date = new_date.replace(day=1)
        build_calendar_ui()
        main_switch.update()

    # ★ (달력) 캘린더 뷰 표시
    def show_calendar_view(e):
        page.calendar_view_date = page.filter_date.replace(day=1)
        build_calendar_ui() 
        main_switch.content = calendar_view_container
        main_switch.update()

    # ★ (수정) 메모 뷰 기간 계산
    def calculate_duration(start_date_str, due_date_str):
        if not start_date_str or not due_date_str: return "" 
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
            delta = (due_date - start_date).days
            if delta < 0: return "기간 오류" 
            elif delta == 0: return " (당일)" 
            else: return f" (총 {delta + 1}일)"
        except ValueError: return "" 

    # ★ (수정) 메모 뷰 표시
    def main_clean(e, item_data):
        memo_text = item_data.get('Memo')
        title_text = item_data.get('Title')
        start_val = item_data.get('Start')
        due_val = item_data.get('Due')
        memo_view_title.value = title_text
        memo_view_duration.value = calculate_duration(start_val, due_val)
        memo_display_text.value = memo_text if memo_text else "저장된 메모가 없습니다."
        main_switch.content = memo_view_container
        main_switch.update() 

    # ★ (수정) 저장 버튼 핸들러
    def save_edit_button_click(e):
        idx = page.editing_item_index
        if idx is None or idx >= len(all_items_data):
            print("오류: 수정할 항목 인덱스가 잘못되었습니다.")
            main_show_list(None)
            return

        if not edit_todo_field.value:
            print("경고: 제목을 입력해주세요.")
            return
        
        original_data = all_items_data[idx]
        
        startVal = edit_start_text.data.strftime('%Y-%m-%d') 
        dueVal = edit_due_checkbox.data.strftime('%Y-%m-%d') if edit_due_checkbox.value and edit_due_checkbox.data else None

        updated_data = {
            'Title': edit_todo_field.value,
            'Start': startVal,
            'Memo': edit_memo_field.value if edit_memo_checkbox.value else None,
            'Link': edit_link_field.value if edit_link_checkbox.value else None,
            'Due': dueVal,
            'NextDay': edit_nextDay.value,
            'Status': original_data.get('Status') 
        }
        
        all_items_data[idx] = updated_data
        print(f"항목 {idx}가 수정되었습니다.")

        page.editing_item_index = None
        update_ui_display()
        main_show_list(None)

    save_edit_button.on_click = save_edit_button_click

    # ★ (수정) 수정 폼 채우기
    def start_editing_item(item_index):
        page.editing_item_index = item_index
        try:
            item_data = all_items_data[item_index]
        except IndexError:
            print(f"오류: 항목 인덱스 {item_index}를 찾을 수 없습니다.")
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
        
        main_switch.content = edit_form_container
        page.update()

    # ★ (수정) 수정 항목 선택 뷰 표시
    def show_edit_selection_view(e):
        edit_selection_list.controls.clear()
        
        filter_date = page.filter_date
        filtered_item_tuples = []
        if filter_date:
            for idx, item in enumerate(all_items_data):
                item_start_str = item.get('Start')
                item_due_str = item.get('Due')
                if not item_start_str: continue
                try:
                    item_start_date = datetime.datetime.strptime(item_start_str, '%Y-%m-%d').date()
                    if item_due_str:
                        item_due_date = datetime.datetime.strptime(item_due_str, '%Y-%m-%d').date()
                        if item_start_date <= filter_date <= item_due_date:
                            filtered_item_tuples.append((idx, item))
                    else:
                        if item_start_date == filter_date:
                            filtered_item_tuples.append((idx, item))
                except ValueError:
                    continue
        
        total_items = len(filtered_item_tuples)
        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
        if total_items == 0: total_pages = 1
        if page.current_page > total_pages: page.current_page = total_pages
        
        start_index = (page.current_page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        
        tuples_to_display = filtered_item_tuples[start_index:end_index]
        pageNum.value = f"{page.current_page}/{total_pages}" 

        if not tuples_to_display:
            edit_selection_list.controls.append(ft.Text("수정할 항목이 없습니다.", color="black"))
        else:
            for i, (actual_idx, item) in enumerate(tuples_to_display):
                display_num = (page.current_page - 1) * ITEMS_PER_PAGE + i + 1
                
                edit_selection_list.controls.append(
                    ft.TextButton(
                        text=f"{display_num}번: {item.get('Title')}",
                        on_click=lambda e, idx=actual_idx: start_editing_item(idx),
                        data=actual_idx, 
                        style=ft.ButtonStyle(color="black") 
                    )
                )

        main_switch.content = edit_selection_container
        page.update()

    # --- ★ [수정] update_ui_display (날짜 필터링 + "이전" 링크 로직) ---
    def update_ui_display():
        try:
            todo_list.controls.clear()
            
            # --- [달력] 날짜 필터링 로직 ---
            filter_date = page.filter_date
            filtered_item_tuples = []
            if filter_date:
                for idx, item in enumerate(all_items_data):
                    item_start_str = item.get('Start')
                    item_due_str = item.get('Due')
                    if not item_start_str: continue
                    try:
                        item_start_date = datetime.datetime.strptime(item_start_str, '%Y-%m-%d').date()
                        if item_due_str:
                            item_due_date = datetime.datetime.strptime(item_due_str, '%Y-%m-%d').date()
                            if item_start_date <= filter_date <= item_due_date:
                                filtered_item_tuples.append((idx, item))
                        else:
                            if item_start_date == filter_date:
                                filtered_item_tuples.append((idx, item))
                    except ValueError as e:
                        print(f"날짜 변환 오류 (항목 {idx}): {e}")
                        continue
            else:
                # 필터가 없으면 모두 표시 (예비 로직)
                filtered_item_tuples = list(enumerate(all_items_data))
            # --- [필터링 끝] ---

            total_items = len(filtered_item_tuples)
            total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
            if total_items == 0: total_pages = 1 
            if page.current_page > total_pages: page.current_page = total_pages
            start_index = (page.current_page - 1) * ITEMS_PER_PAGE
            end_index = start_index + ITEMS_PER_PAGE
            
            tuples_to_display = filtered_item_tuples[start_index:end_index] # 필터링된 목록에서 페이징
            pageNum.value = f"{page.current_page}/{total_pages}"

            for actual_idx, item in tuples_to_display: # (actual_idx는 원본 인덱스)
                title_text = item.get('Title', '')
                due_val = item.get('Due', None)
                memo_val = item.get('Memo')
                link_val = item.get('Link')
                status = item.get('Status', None)
                
                # --- ★ [원본 로직] link_val이 None이어도 항상 딕셔너리 반환 ---
                pre_link = Todo_def.url_mention(link_val)

                def create_status_handler(item_idx, dic_value):
                    def on_status_select(e):
                        all_items_data[item_idx]['Status'] = e.control.text
                        update_ui_display()
                    return on_status_select

                status_display = status if status else "▢"
                status_popup = ft.PopupMenuButton(
                    content=ft.Text(value=status_display, size=16, weight="w500", color="black"),
                    items=[
                        ft.PopupMenuItem(text="O", on_click=create_status_handler(actual_idx, 1)),
                        ft.PopupMenuItem(text="△", on_click=create_status_handler(actual_idx, 2)),
                        ft.PopupMenuItem(text="X", on_click=create_status_handler(actual_idx, 3)),
                    ], tooltip='complete'
                )
                
                # --- ★ [원본 로직] 'memo.png' 사용 (assets 폴더 필요) ---
                memo_button = ft.IconButton(
                    content=ft.Image(src='memo.png', width=12, height=12),
                    opacity=1.0 if memo_val else 0.0,
                    tooltip="메모 보기",
                    on_click=lambda e, item_ref=item: main_clean(e, item_ref),
                    width=30, height=30
                )
                # --- [원본 로직 끝] ---

                title_row = ft.Row(
                    controls=[
                        status_popup,
                        ft.Text(value=title_text, size=16, weight="w500", color="black"),
                        ft.Container(expand=True), memo_button
                    ], vertical_alignment="center", spacing=5
                )
                due_text_control = ft.Text(
                    value=f"Due: {due_val}" if due_val else " ", 
                    size=11, color="black", # 'grey_700'에서 'black'으로 (다크모드)
                    opacity=1.0 if due_val else 0.0 
                )
                
                # --- ★ [수정] 'link_val'을 이용한 링크/파비콘 처리 ---
          
                # 동적으로 컨트롤을 담을 리스트
                link_controls_list = []
                
                # 클릭 이벤트와 툴팁은 pre_link의 'url'을 기반으로 설정
                actual_url = pre_link.get('url')
                click_handler = (lambda _, url=actual_url: page.launch_url(url) if url else None)
                tooltip_text = f"링크 열기: {actual_url}" if actual_url else None

                if link_val: # 링크 값이 실제로 존재하는 경우에만
                    favicon_url = pre_link.get('favicon_url')
                    link_title = pre_link.get('title')

                    if favicon_url:
                        # 1. 파비콘이 있으면: 파비콘 + 타이틀
                        link_controls_list.append(
                            ft.Image(
                                src=favicon_url, # 이 시점에는 None이 아님
                                width = 12, height = 12
                            )
                        )
                        link_controls_list.append(
                            ft.Text(
                                link_title,
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color="black"
                            )
                        )
                    elif actual_url:
                        # 2. 파비콘은 없고 URL만 있으면: URL 텍스트 (사용자 요청)
                        link_controls_list.append(
                            ft.Text(
                                actual_url, # URL 자체를 텍스트로 표시
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color="blue", # 하이퍼링크처럼 보이도록
                                italic=True
                            )
                        )
                    # (else: link_val은 있지만 pre_link가 아무것도 반환 안하면 리스트는 비어있음)

                # --- [수정된 부분] ---
                icon_row_contents = ft.Row(
                    controls=link_controls_list, # 동적으로 채워진 리스트 사용
                    spacing=5,
                    vertical_alignment=ft.CrossAxisAlignment.START
                )
                
                # --- ★ [레이아웃 붕괴 방지 수정] ---
                icon_row_controls = ft.Container(
                    content=icon_row_contents,
                    on_click=click_handler, # 핸들러 연결
                    tooltip=tooltip_text,   # 툴팁 연결
                    padding=0,
                    height=14,  # 고정 높이를 주어 공간을 항상 차지하도록 함
                    opacity=1.0 if link_val else 0.0, # visible 대신 opacity 사용
                )
                # --- ★ [수정 끝] ---
                
                new_item_controls = [title_row, due_text_control, icon_row_controls]
                new_item = ft.Container(
                    content=ft.Column(controls=new_item_controls, spacing=1, tight=True),
                    padding=ft.padding.only(left=10, top=8, right=10, bottom=8),
                    bgcolor='#F5F5F5', border_radius=5, border=ft.border.all(1, '#E0E0E0')
                )
                todo_list.controls.append(new_item)

            page.update() 
            
            if main_switch.content != list_view_container:
                print("다른 뷰(메모/달력)가 활성 중이므로, 목록 UI는 백그라운드에서 갱신됨.")
            print(f"UI 업데이트 완료. 현재 {page.current_page}/{total_pages} 페이지 표시 (필터링된 항목 기준).")

        except Exception as e:
            print(f"!!!!!!!! update_ui_display 함수 전체에서 치명적인 오류 발생: {e} !!!!!!!!")
            # 오류 발생 시 사용자에게 알림
            todo_list.controls.clear()
            todo_list.controls.append(ft.Text(f"오류: {e}", color="red"))
            page.update()

    # --- ★ [스레드] PubSub 핸들러 ---
    def handle_new_data(message): 
        data = message 
        all_items_data.append(data)
        print(f"항목 추가됨 (백그라운드): {data.get('Title')}")
        
        # 메인 스레드에서 안전하게 UI 업데이트
        update_ui_display() 
        
        if main_switch.content == calendar_view_container:
            print("달력 뷰가 열려있으므로, UI를 갱신합니다.")
            build_calendar_ui()
            main_switch.update()

    # --- ★ [스레드] check_queue (PubSub 사용) ---
    def check_queue(queue_to_check: multiprocessing.Queue):
        while True:
            try:
                data = queue_to_check.get(timeout=0.5) 
                
                # 메인 스레드로 UI 업데이트 요청
                page.pubsub.send_all(data) 
                
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Queue 확인 중 오류: {e}")
                time.sleep(0.5)

    # --- ★ [수정] 페이징 핸들러 (뷰 상태 인지) ---
    def on_page_left(e):
        if page.current_page > 1:
            page.current_page -= 1
            if main_switch.content == edit_selection_container:
                show_edit_selection_view(None)
            else:
                update_ui_display() 

    def on_page_right(e):
        # 현재 뷰의 총 페이지 수 계산
        filter_date = page.filter_date
        filtered_item_count = 0
        if filter_date:
            for item in all_items_data:
                item_start_str = item.get('Start')
                item_due_str = item.get('Due')
                if not item_start_str: continue
                try:
                    item_start_date = datetime.datetime.strptime(item_start_str, '%Y-%m-%d').date()
                    if item_due_str:
                        item_due_date = datetime.datetime.strptime(item_due_str, '%Y-%m-%d').date()
                        if item_start_date <= filter_date <= item_due_date:
                            filtered_item_count += 1
                    else:
                        if item_start_date == filter_date:
                            filtered_item_count += 1
                except ValueError: continue
        total_items = filtered_item_count 
        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
        if total_items == 0: total_pages = 1
            
        if page.current_page < total_pages:
            page.current_page += 1
            if main_switch.content == edit_selection_container:
                show_edit_selection_view(None)
            else:
                update_ui_display() 

    def open_add_window(e):
        if page.add_window_process and page.add_window_process.is_alive():
            alert_dialog = ft.AlertDialog(
                modal=True, title=ft.Text("Warning"),
                content=ft.Text("Add 윈도우가 이미 열려있습니다."),
                actions=[ft.TextButton("확인", on_click=lambda e: page.close(alert_dialog))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(alert_dialog)
        else:
            print("Add 윈도우를 별도 프로세스로 엽니다...")
            p = multiprocessing.Process(target=start_add_window_app, args=(main_queue,))
            p.start()
            page.add_window_process = p

    # --- 페이지 레이아웃 설정 ---
    page.title = 'PySchedule'
    page.window.width = 585
    page.window.height = 365
    page.window.resizable = False
    page.window.maximizable = False
    page.padding = 0
    page.bgcolor = '#FFFFFF'
    page.add_window_process = None
    
    # --- ★ [원본 로직] ft.Image 사용 ---
    pageBtn_L = ft.IconButton(
        content=ft.Image(src='Left.png', width=15, height=15),
        tooltip='Left', width=25, height=25,
        on_click=on_page_left 
    )
    pageNum = ft.Text(value='1/1', size=10, weight=ft.FontWeight.W_500, color='black')
    pageBtn_R = ft.IconButton(
        content=ft.Image(src='Right.png', width=15, height=15),
        tooltip='Right', width=25, height=25,
        on_click=on_page_right 
    )
    
    # --- ★ [원본 로직] ft.Image 사용 (사이드바) ---
    sidebar = ft.Container(
        width=90, height=450, bgcolor='#D9D9D9',
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                sidebar_month_text, # (달력) 변수 사용
                sidebar_day_text,   # (달력) 변수 사용
                ft.Container(height=20),
                ft.IconButton(
                    content=ft.Image(src='Add.png', width=25, height=25), 
                    on_click=open_add_window, tooltip='add'
                ),
                ft.Container(height=15),
                ft.IconButton(
                    content=ft.Image(src='Canlender.png', width=25, height=25), 
                    tooltip='calender',
                    on_click=show_calendar_view # (달력) 핸들러 연결
                ),
                ft.Container(height=15),
                ft.IconButton(
                    content=ft.Image(src='edit.png', width=20, height=20), 
                    tooltip='edit',
                    on_click=show_edit_selection_view # (수정) 핸들러 연결
                ),
                ft.Container(expand=True),
                ft.Row(
                    controls=[pageBtn_L, pageNum, pageBtn_R],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=5
                ),
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0
        )
    )

    layout = ft.Row(controls=[sidebar, main_switch], spacing=0, expand=True)
    page.add(layout)
    
    # --- ★ [스레드] PubSub 구독 ---
    page.pubsub.subscribe(handle_new_data)
    
    update_ui_display()
    
    queue_thread = threading.Thread(target=check_queue, args=(main_queue,), daemon=True)
    queue_thread.start()


if __name__ == "__main__":
    data_queue = multiprocessing.Queue()
    
    ft.app(target=lambda p: main(p, data_queue))