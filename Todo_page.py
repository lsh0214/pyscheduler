import flet as ft
import datetime
import Todo_def  # 사용자 정의 모듈
import calendar
from dateutil.relativedelta import relativedelta

def main(page: ft.Page):
    
    all_items_data = [] 
    page.current_page = 1 
    ITEMS_PER_PAGE = 3
    page.editing_item_index = None 

    page.calendar_view_date = datetime.date.today()
    pre_to_day = datetime.date.today()
    page.filter_date = pre_to_day 

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
                            content=ft.Image(src='Left.png',width=15, height=15),
                            on_click=lambda e: change_month(e, -1)
                        ),
                        ft.Container(
                            content=calendar_header_text, 
                            alignment=ft.alignment.center
                        ),
                        ft.IconButton(
                            content=ft.Image(src='Right.png', width=15, height=15),
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
    
    save_edit_button = ft.TextButton('저장')
    
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
                ft.Row(
                    controls=[ft.Container(expand=True), cancel_edit_button, save_edit_button],
                    alignment=ft.MainAxisAlignment.END # 버튼 오른쪽 정렬
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.START
        ),
        padding=ft.padding.all(20),
        expand=True
    )
    
    # --- 6. 일정 추가 폼 뷰 (Add Form View) ---

    def add_start_select_Day(e):
        selected_date = e.control.value
        print(f"선택된 날짜: {selected_date.strftime('%Y-%m-%d')}")
        add_start_button.data = selected_date
        add_start_button.text = selected_date.strftime('%Y-%m-%d')
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
        add_due_checkbox.value = False # 날짜 선택 안하고 닫으면 체크 해제
        page.update()
        print("날짜가 선택되지 않아 마감 체크를 해제합니다.")

    add_due_picker = ft.DatePicker(
        on_change=add_due_select_Day,
        on_dismiss=add_due_date_dismissal
    )
    
    # DatePicker들을 메인 페이지의 오버레이에 추가
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
        
        if e.control.value: # 체크박스가 True가 될 때
            if add_start_button.data: # 시작일이 선택되었는지 확인
                add_due_picker.first_date = add_start_button.data
                add_due_picker.value = add_start_button.data
                page.open(add_due_picker)
            else:
                # 시작일이 선택되지 않았으면 경고
                start_alert = ft.AlertDialog(
                    modal=True, title=ft.Text("경고"),
                    content=ft.Text("시작일을 선택해주세요."),
                    actions=[ft.TextButton("확인", on_click=not_have_start)],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(start_alert)
                return
        else: # 체크박스가 False가 될 때
            add_due_checkbox.data = None
            page.update()
    
    # 폼 리셋 함수
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
        # page.update()는 호출한 쪽(save_data)에서 처리
    
    def add_save_data(e):
        # 유효성 검사 (기존 add_window의 save_data 로직)
        if not add_todo_field.value:
            title_alert = ft.AlertDialog(
                modal=True, title=ft.Text("경고"),
                content=ft.Text("제목(Title)을 입력해주세요."),
                actions=[ft.TextButton("확인", on_click=lambda e: page.close(title_alert))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(title_alert)
            return
        
        # --- 제목 길이 검사 ---
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
        # --- 길이 검사 끝 ---
            
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

        # 데이터 생성
        startVal = add_start_button.data.strftime('%Y-%m-%d') if add_start_button.data else None
        dueVal = add_due_checkbox.data.strftime('%Y-%m-%d') if add_due_checkbox.value and add_due_checkbox.data else None

        check_save_data = {
            'Title': add_todo_field.value,
            'Start': startVal,
            'Memo': add_memo_field.value if add_memo_checkbox.value else None,
            'Link': add_link_field.value if add_link_checkbox.value else None,
            'Due': dueVal,
            'NextDay': add_nextDay_checkbox.value,
            'Status': None
        }
        print("--- 저장 시작 ---")
        print(check_save_data)

        # 메인 리스트에 직접 추가
        all_items_data.append(check_save_data)
        print("항목이 메인 리스트에 직접 추가되었습니다.")
        
        # UI 갱신 및 폼 리셋
        reset_add_form() # 폼 필드 초기화
        
        # 새 항목이 추가되었으므로, 해당 항목이 보이도록 필터 날짜를 변경하고 UI 갱신
        page.filter_date = datetime.datetime.strptime(startVal, '%Y-%m-%d').date()
        sidebar_month_text.value = page.filter_date.strftime("%m.")
        sidebar_day_text.value = page.filter_date.strftime("%d")
        page.current_page = 1 # 새 항목을 보려면 1페이지로
        
        update_ui_display() # 목록 뷰 갱신
        main_show_list(None) # 목록 뷰로 전환 (page.update() 포함됨)

    # (추가) UI 컨트롤 정의
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
        on_click=lambda e: main_show_list(None) or reset_add_form(), # 취소 시 폼 리셋
        style=ft.ButtonStyle(color="black")
    )

    # (추가) 컨테이너 정의
    add_form_container = ft.Container(
        content=ft.Column(
            controls=[
                add_title, add_todo_field, add_start_button, add_due_checkbox,
                add_memo_checkbox, add_memo_field,
                add_link_checkbox, add_link_field, add_nextDay_checkbox,
                ft.Row(
                    controls=[ft.Container(expand=True), add_cancel_button, add_save_button],
                    alignment=ft.MainAxisAlignment.END # 버튼 오른쪽 정렬
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
        # on_click은 아래 on_page_left 함수 정의 후에 설정
    )
    pageNum = ft.Text(value='1/1', size=10, weight=ft.FontWeight.W_500, color='black')
    pageBtn_R = ft.IconButton(
        content=ft.Image(src='Right.png', width=15, height=15),
        tooltip='Right', width=25, height=25,
        # on_click은 아래 on_page_right 함수 정의 후에 설정
    )

    # 페이지네이션 컨트롤을 묶어서 관리할 Row 객체
    pagination_row = ft.Row(
        controls=[pageBtn_L, pageNum, pageBtn_R],
        alignment=ft.MainAxisAlignment.CENTER, spacing=5,
        visible=True # 기본값은 True (보이게)
    )
    # === 뷰 전환 및 핸들러 함수 ===
    
    def main_show_list(e):
        page.window.height = 365
        main_switch.content = list_view_container
        page.editing_item_index = None
        pagination_row.visible = True
        main_switch.update()
        page.update()
    
    # '일정 추가' 뷰 표시 함수
    def show_add_form_view(e):
        page.window.height = 365
        pagination_row.visible = False
        reset_add_form()
        main_switch.content = add_form_container
        main_switch.update()
        page.update()

    back_to_list_button.on_click = main_show_list
    back_to_list_from_cal.on_click = main_show_list

    # 캘린더 UI 생성 함수 (이벤트 점 포함)
    # 캘린더 UI 생성 함수 (이벤트 점 포함)
    def build_calendar_ui():
        calendar.setfirstweekday(calendar.SUNDAY)
        year = page.calendar_view_date.year
        month = page.calendar_view_date.month
        calendar_header_text.value = f"{year}년 {month}월"
        calendar_days_container.controls.clear()
        
        # --- 👇 [핵심 수정] ---
        today = datetime.date.today()
        selected_date = page.filter_date # '오늘'이 아닌 '선택된 날짜'
        # --- [수정 끝] ---
        
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
                    # --- 👇 [핵심 수정] ---
                    current_day_date = datetime.date(year, month, day) # [신규]
                    is_today = (current_day_date == today) # [수정]
                    is_selected = (current_day_date == selected_date) # [신규]
                    
                    # 1. 기본 텍스트 색상 (요일별)
                    text_color = "red" if day_idx == 0 else ("blue" if day_idx == 6 else "black")
                    
                    # 2. 기본 배경/테두리/굵기
                    bgcolor = "transparent" # 기본 배경 투명
                    border = None
                    text_weight = "normal"
                    
                    # 3. '오늘' 날짜 스타일 (선택되지 않았을 때)
                    if is_today and not is_selected:
                        bgcolor = "transparent"
                        border = ft.border.all(1, "#3E91E4") # 파란 테두리
                        text_color = "#3E91E4"
                        text_weight = "bold"
                    
                    # 4. '선택된' 날짜 스타일 (오늘이든 아니든 덮어씀)
                    if is_selected:
                        bgcolor = "#1976D2" # 파란 배경
                        border = None
                        text_color = "white" # 흰색 텍스트
                        text_weight = "bold"

                    day_content = ft.Container(
                        content=ft.Text(value=str(day), size=12, weight=text_weight, color=text_color),
                        alignment=ft.alignment.center, width=30, height=30,
                        bgcolor=bgcolor, border=border, border_radius=15,
                    )
                    # --- [수정 끝] ---
                    
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
        main_switch.update()

    # 캘린더 뷰 표시
    def show_calendar_view(e):
        page.window.height = 385 #-----------------------------------------------------캘린더 높이 최적화
        pagination_row.visible = False
        page.calendar_view_date = page.filter_date.replace(day=1)
        build_calendar_ui() 
        main_switch.content = calendar_view_container
        main_switch.update()
        page.update()

    # 메모 뷰 기간 계산
    # [수정] 메모 뷰 기간 계산 (D-Day 계산 로직으로 변경)
    def calculate_duration(reference_date, due_date_str):
        """
        기준 날짜(reference_date)로부터 마감일(due_date_str)까지의 D-Day를 계산합니다.
        """
        
        # 마감일이 없으면 D-Day를 표시하지 않음
        if not due_date_str:
            return "" 

        try:
            # --- 👇 [핵심 수정 1] ---
            # 기준 날짜 (page.filter_date 객체)
            start_date = reference_date # (이 인수는 이미 date 객체임)
            # 마감일 (문자열)
            due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
            # --- [수정 끝] ---
            
            # (마감일 - 기준일)
            delta = (due_date - start_date).days
            
            if delta < 0:
                return f"(D+{-delta}일)"
            elif delta == 0:
                return "(D-Day)"
            else:
                return f"(D-{delta}일)"
        except ValueError:
            return "" # 날짜 형식 오류
        except TypeError: # [추가] 혹시 모를 타입 오류 방지
            print(f"calculate_duration 타입 오류: {reference_date}, {due_date_str}")
            return ""

    # 메모 뷰 표시
    def main_clean(e, item_data):
        memo_text = item_data.get('Memo')
        title_text = item_data.get('Title')
        start_val = item_data.get('Start') # (D-Day 계산에 사용 안 함)s
        due_val = item_data.get('Due')
        
        memo_view_title.value = title_text
        
        # --- 👇 [핵심 수정 2] ---
        # calculate_duration의 첫 번째 인수로 'page.filter_date' (기준일) 전달
        # 두 번째 인수로 'due_val' (마감일 문자열) 전달
        memo_view_duration.value = calculate_duration(page.filter_date, due_val)
        # --- [수정 끝] ---
        
        memo_display_text.value = memo_text if memo_text else "저장된 메모가 없습니다."
        pagination_row.visible = False
        main_switch.content = memo_view_container
        main_switch.update()

    # 수정 저장 버튼 핸들러
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

    # 수정 폼 채우기
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

        pagination_row.visible = False
        
        main_switch.content = edit_form_container
        page.update()

    # 수정 항목 선택 뷰 표시
    def show_edit_selection_view(e):
        page.window.height = 365
        pagination_row.visible = True
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

    # --- UI 갱신 함수 (메인 리스트) ---
    def update_ui_display():
        try:
            todo_list.controls.clear()
            
            # --- 날짜 필터링 로직 ---
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
                filtered_item_tuples = list(enumerate(all_items_data))
            # --- 필터링 끝 ---

            total_items = len(filtered_item_tuples)
            total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
            if total_items == 0: total_pages = 1 
            if page.current_page > total_pages: page.current_page = total_pages
            start_index = (page.current_page - 1) * ITEMS_PER_PAGE
            end_index = start_index + ITEMS_PER_PAGE
            
            tuples_to_display = filtered_item_tuples[start_index:end_index]
            pageNum.value = f"{page.current_page}/{total_pages}"

            for actual_idx, item in tuples_to_display:
                title_text = item.get('Title', '')
                start_val = item.get('Start', None)
                due_val = item.get('Due', None)
                memo_val = item.get('Memo')
                link_val = item.get('Link')
                status = item.get('Status', None)
                
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
                
                memo_button = ft.IconButton(
                    content=ft.Image(src='memo.png', width=12, height=12),
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
                # --- 👇 [핵심 수정 2] ---
                # D-Day 계산을 (page.filter_date -> due_val)로 변
                dday_text = calculate_duration(page.filter_date, due_val)

                due_text_control = ft.Text(
                    # [수정] Due: (마감일) (D-n) 형태로 표시
                    value=f"Due: {due_val} {dday_text}" if due_val else " ", 
                    size=11, color="black", 
                    opacity=1.0 if due_val else 0.0 
                )
                # --- [수정 끝] ---
                
                # --- 링크/파비콘 처리 (opacity + height) ---
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
                    height=16,  # 고정 높이
                    opacity=1.0 if link_val else 0.0, # opacity 사용
                )
                # --- 링크 처리 끝 ---
                
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
    pageBtn_L.on_click = on_page_left
    pageBtn_R.on_click = on_page_right

    # --- 페이지 레이아웃 설정 ---
    page.title = 'PySchedule'
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
                    # 'Add' 버튼 클릭 시 show_add_form_view 호출
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