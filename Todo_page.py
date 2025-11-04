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

    page.calendar_view_date = datetime.date.today()

    # 오늘 날짜를 기본 필터 날짜로 설정
    pre_toDay = datetime.date.today()
    page.filter_date = pre_toDay  # <-- (1) 필터 상태를 저장할 변수

    # (2) 사이드바의 날짜 Text 컨트롤을 변수로 미리 정의
    sidebar_month_text = ft.Text(
        value=pre_toDay.strftime("%m."), 
        size=20, weight=ft.FontWeight.W_500, color='#000000'
    )
    sidebar_day_text = ft.Text(
        value=pre_toDay.strftime("%d"), 
        size=25, weight=ft.FontWeight.W_500, color='#000000'
    )

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
    
    # === 달력 뷰 컨트롤 ===
    
    calendar_header_text = ft.Text(
        value="",
        size=18,
        weight="bold",
        color="black"
    )
    
    weekdays = ["일", "월", "화", "수", "목", "금", "토"]
    weekday_colors = ["red", "black", "black", "black", "black", "black", "blue"]
    
    calendar_weekday_row = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(
                    weekdays[i], 
                    size=12,
                    weight="bold",
                    color=weekday_colors[i]
                ),
                width=40,
                height=25,
                alignment=ft.alignment.center
            ) for i in range(7)
        ],
        spacing=0,
        alignment=ft.MainAxisAlignment.CENTER
    )

    calendar_days_container = ft.Column(
        controls=[],
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    back_to_list_from_cal = ft.TextButton(
        "이전",
        width=50, height=30,
        tooltip="목록으로 돌아가기"
    )
    
    # --- [START] build_calendar_ui 함수 (이벤트 점 포함) ---
    def build_calendar_ui():
        calendar.setfirstweekday(calendar.SUNDAY)
        
        year = page.calendar_view_date.year
        month = page.calendar_view_date.month
        
        calendar_header_text.value = f"{year}년 {month}월"
        calendar_days_container.controls.clear()
        
        # 이 달에 일정이 있는지 미리 검사
        events_on_day = {} # {1: True, 5: True, ...}
        for item in all_items_data:
            item_start_str = item.get('Start')
            if not item_start_str:
                continue
            
            try:
                item_start_date = datetime.datetime.strptime(item_start_str, '%Y-%m-%d').date()
                item_due_str = item.get('Due')

                if item_due_str:
                    # 마감일이 있는 경우 (기간)
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
                    # 마감일이 없는 경우 (하루)
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
                    is_today = (
                        day == datetime.date.today().day and 
                        month == datetime.date.today().month and 
                        year == datetime.date.today().year
                    )
                    
                    text_color = "white" if is_today else (
                        "red" if day_idx == 0 else (
                            "blue" if day_idx == 6 else "black"
                        )
                    )
                    
                    # 날짜 컨테이너에 이벤트 표시 추가
                    day_content = ft.Container(
                        content=ft.Text(
                            value=str(day), 
                            size=12,
                            weight="bold" if is_today else "normal",
                            color=text_color
                        ),
                        alignment=ft.alignment.center,
                        width=30, 
                        height=30,
                        bgcolor="#1976D2" if is_today else None,
                        border_radius=15,
                    )
                    
                    has_event = events_on_day.get(day, False)
                    
                    event_dot = ft.Container(
                        width=5,
                        height=5,
                        bgcolor="red" if has_event else "transparent", # 이벤트 있으면 빨간 점
                        border_radius=2.5,
                        margin=ft.margin.only(top=1) 
                    )
                    
                    day_stack = ft.Column(
                        controls=[
                            day_content,
                            event_dot
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER, # <--- 대문자로 수정됨
                        height=38 
                    )

                    week_row_controls.append(
                        ft.Container(
                            content=day_stack, 
                            alignment=ft.alignment.top_center, 
                            width=40,
                            height=38,
                            on_click=lambda e, d=day: on_calendar_day_click(d),
                            ink=True
                        )
                    )
            
            calendar_days_container.controls.append(
                ft.Row(
                    controls=week_row_controls,
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
    # --- [END] build_calendar_ui 함수 ---

    def on_calendar_day_click(day):
        selected_date = page.calendar_view_date.replace(day=day)
        print(f"달력 날짜 클릭: {selected_date.strftime('%Y-%m-%d')}")

        page.filter_date = selected_date
        sidebar_month_text.value = selected_date.strftime("%m.")
        sidebar_day_text.value = selected_date.strftime("%d")
        page.current_page = 1
        update_ui_display()
        main_show_list(None)

    def change_month(e, delta):
        current_date = page.calendar_view_date
        new_date = current_date + relativedelta(months=delta)
        page.calendar_view_date = new_date.replace(day=1)
        
        build_calendar_ui()
        main_switch.update()

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
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Container(height=10),
                calendar_weekday_row,
                ft.Container(height=5),
                calendar_days_container,
                ft.Row(
                    controls=[
                        ft.Container(expand=True),
                        back_to_list_from_cal
                    ]
                )
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=20), 
        expand=True, 
        alignment=ft.alignment.top_center
    )
    
    # === 뷰 전환 로직 ===

    main_switch = ft.AnimatedSwitcher(
        content=list_view_container,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
        reverse_duration=200,
        expand=True
    )
    
    def main_show_list(e):
        main_switch.content = list_view_container
        main_switch.update()
    
    back_to_list_button.on_click = main_show_list
    back_to_list_from_cal.on_click = main_show_list

    def show_calendar_view(e):
        page.calendar_view_date = page.filter_date.replace(day=1)
        build_calendar_ui() 
        main_switch.content = calendar_view_container
        main_switch.update()

    def calculate_duration(start_date_str, due_date_str):
        if not start_date_str or not due_date_str:
            return "" 
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
            delta = (due_date - start_date).days
            if delta < 0:
                return "기간 오류" 
            elif delta == 0:
                return " (당일)" 
            else:
                total_days = delta + 1
                return f" (총 {total_days}일)"
        except ValueError:
            return "" 

    def main_clean(e, item_data):
        memo_text = item_data.get('Memo')
        title_text = item_data.get('Title')
        start_val = item_data.get('Start')
        due_val = item_data.get('Due')

        memo_view_title.value = title_text
        memo_view_duration.value = calculate_duration(start_val, due_val)
        
        if not memo_text: 
            memo_display_text.value = "저장된 메모가 없습니다."
        else:
            memo_display_text.value = memo_text
        
        main_switch.content = memo_view_container
        main_switch.update() 

    # --- [START] update_ui_display 함수 (기간 필터링) ---
    def update_ui_display():
        
        todo_list.controls.clear()

        filter_date = page.filter_date
        filtered_item_tuples = [] 
        
        if filter_date:
            for idx, item in enumerate(all_items_data):
                item_start_str = item.get('Start')
                item_due_str = item.get('Due')
                
                if not item_start_str:
                    continue

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
            filtered_item_tuples = list(enumerate(all_items_data))

        total_items = len(filtered_item_tuples)
        
        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
        if total_items == 0:
            total_pages = 1 
        if page.current_page > total_pages:
            page.current_page = total_pages
        
        start_index = (page.current_page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        
        tuples_to_display = filtered_item_tuples[start_index:end_index]
        pageNum.value = f"{page.current_page}/{total_pages}"

        for actual_idx, item in tuples_to_display:
            
            title_text = item.get('Title', '')
            due_val = item.get('Due', None)
            memo_val = item.get('Memo')
            link_val = item.get('Link')
            status = item.get('Status', None)
            
            if link_val:
                pre_link = Todo_def.url_mention(link_val)
                if pre_link is None:
                    pre_link = {} 
            else:
                pre_link = {} 

            def create_status_handler(item_idx, dic_value):
                def on_status_select(e):
                    selected_status = e.control.text
                    all_items_data[item_idx]['Status'] = selected_status
                    print(f"항목 {item_idx}의 상태를 {selected_status}로 변경")
                    print(f"딕셔너리 value = {dic_value}") 
                    update_ui_display() 
                return on_status_select

            status_display = status if status else "▢"
            
            status_popup = ft.PopupMenuButton(
                content=ft.Text(
                    value=status_display,
                    size=16,
                    weight="w500",
                    color='black'
                ),
                items=[
                    ft.PopupMenuItem(text="O", on_click=create_status_handler(actual_idx, 1)),
                    ft.PopupMenuItem(text="△", on_click=create_status_handler(actual_idx, 2)),
                    ft.PopupMenuItem(text="X", on_click=create_status_handler(actual_idx, 3)),
                ], 
                tooltip='complete'
            )
            
            memo_button = ft.IconButton(
                content=ft.Image(src='memo.png', width=12, height=12),
                opacity=1.0 if memo_val else 0.0,
                tooltip="메모 보기",
                on_click=lambda e, item_ref=item: main_clean(e, item_ref),
                width=30,
                height=30
            )
            
            title_row = ft.Row(
                controls=[
                    status_popup,
                    ft.Text(
                        value=title_text, 
                        size=16, 
                        weight="w500",
                        color='black'
                    ),
                    ft.Container(expand=True),
                    memo_button
                ],
                vertical_alignment="center",
                spacing=5
            )

            due_text_control = ft.Text(
                value=f"Due: {due_val}" if due_val else " ", 
                size=11, 
                color='black',
                opacity=1.0 if due_val else 0.0 
            )
            
            if link_val:
                pre_link = Todo_def.url_mention(link_val)
                title = pre_link.get('title')
                url = pre_link.get('url')
                
                if not url or not url.startswith("https://"):
                    print("링크가 없거나, 'https://'로 시작하지 않습니다.")
                    icon_row_controls = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    value="URL 형식이 잘못되었습니다",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color="red"
                                )
                            ],
                            spacing=5,
                            height=16
                        ),
                        padding=0
                    )
                else:
                    favicon_url = pre_link.get('favicon_url')
                    
                    if favicon_url:
                        icon_row_content = ft.Row(
                            controls=[
                                ft.Image(
                                    src=favicon_url,
                                    width=12,
                                    height=12
                                ),
                                ft.Text(
                                    value=title,
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color='black'
                                )
                            ],
                            spacing=5,
                            height=16,
                            vertical_alignment=ft.CrossAxisAlignment.BASELINE
                        )
                    else:
                        icon_row_content = ft.Row(
                            controls=[
                                ft.Container(width=12),
                                ft.Text(
                                    value=title,
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color='black'
                                )
                            ],
                            spacing=5,
                            height=16,
                            vertical_alignment=ft.CrossAxisAlignment.BASELINE
                        )
                        
                    icon_row_controls = ft.Container(
                        content=icon_row_content,
                        on_click=lambda _, u=url: page.launch_url(u) if u and u != "None" else None,
                        tooltip=f"링크 열기: {url}" if url and url != "None" else None,
                        padding=0
                    )
            else:
                icon_row_controls = ft.Row(
                    controls=[ft.Text(' ')],
                    height=16,
                    spacing=5,
                    opacity=0.0
                )
            
            new_item_controls = [
                title_row, due_text_control, icon_row_controls
            ]
            
            new_item = ft.Container(
                content=ft.Column(controls=new_item_controls, spacing=1, tight=True),
                padding=ft.padding.only(left=10, top=8, right=10, bottom=8),
                bgcolor='#F5F5F5',
                border_radius=5,
                border=ft.border.all(1, '#E0E0E0')
            )
            
            todo_list.controls.append(new_item)

        page.update()

        if main_switch.content != list_view_container:
            print("다른 뷰(메모/달력)가 활성 중이므로, 목록 UI는 백그라운드에서 갱신됨.")
            
        print(f"UI 업데이트 완료. 현재 {page.current_page}/{total_pages} 페이지 표시 (필터링된 항목 기준).")
    # --- [END] update_ui_display 함수 ---

    # --- [START] check_queue 함수 (날짜 점프 방지) ---
    def check_queue(queue_to_check: multiprocessing.Queue):
        while True:
            try:
                data = queue_to_check.get(timeout=0.5) 
                
                all_items_data.append(data)
                print(f"항목 추가됨 (백그라운드): {data.get('Title')}")
                
                # 현재 뷰를 새로고침 (날짜 이동 없음)
                update_ui_display() 
                
                # 만약 달력 뷰가 열려있다면, '점'을 갱신
                if main_switch.content == calendar_view_container:
                    print("달력 뷰가 열려있으므로, UI를 갱신합니다.")
                    build_calendar_ui()
                    main_switch.update() 
                
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Queue 확인 중 오류: {e}")
                time.sleep(0.5)
    # --- [END] check_queue 함수 ---

    # --- [START] NameError 수정을 위해 함수 정의를 위로 이동 ---
    def on_page_left(e):
        if page.current_page > 1:
            page.current_page -= 1
            update_ui_display() 

    def on_page_right(e):
        # 페이지 계산을 위해 필터링된 항목 수 계산
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
                except ValueError:
                    continue
        
        total_items = filtered_item_count 
        
        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
        if total_items == 0: total_pages = 1
            
        if page.current_page < total_pages:
            page.current_page += 1
            update_ui_display() 
    # --- [END] 함수 정의 이동 ---

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

    page.title = 'PySchedule'
    page.window.width = 585
    page.window.height = 365
    page.window.resizable = False
    page.window.maximizable = False
    page.padding = 0
    page.bgcolor = '#FFFFFF'
    page.add_window_process = None
    
    # --- [START] 버튼 생성 (이제 함수가 정의된 뒤에 실행됨) ---
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
    # --- [END] 버튼 생성 ---
    
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
                    on_click=open_add_window, tooltip='add'
                ),
                ft.Container(height=15),
                ft.IconButton(
                    content=ft.Image(src='Canlender.png', width=25, height=25), 
                    tooltip='calender',
                    on_click=show_calendar_view
                ),
                ft.Container(height=15),
                ft.IconButton(content=ft.Image(src='edit.png', width=20, height=20), tooltip='edit'),
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
    
    update_ui_display()
    
    queue_thread = threading.Thread(target=check_queue, args=(main_queue,), daemon=True)
    queue_thread.start()


if __name__ == "__main__":
    data_queue = multiprocessing.Queue()
    
    ft.app(target=lambda p: main(p, data_queue))