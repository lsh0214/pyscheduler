import flet as ft
import multiprocessing
import datetime
import threading
import time
import queue  
import Todo_def

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
            'Status': None  # 초기 상태는 None
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

# (main 함수가 시작되는 부분)
def main(page: ft.Page, main_queue: multiprocessing.Queue):
    
    # --- [데이터 및 상태 변수] ---
    all_items_data = [] 
    page.current_page = 1 
    ITEMS_PER_PAGE = 3    

    # --- [신규] UI 컨트롤 미리 정의 ---
    
    # 1. '할 일 목록' 뷰 (사용자 코드의 todo_list)
    todo_list = ft.Column(
        controls=[], scroll=ft.ScrollMode.AUTO, spacing=7,
        horizontal_alignment=ft.CrossAxisAlignment.START, expand=True
    )
    # [신규] todo_list를 감싸는 컨테이너
    list_view_container = ft.Container(
        content=todo_list, 
        padding=ft.padding.all(20), 
        expand=True, 
        alignment=ft.alignment.top_left
    )
    
    # 2. '메모 상세' 뷰 (새로 추가)
    memo_display_text = ft.Text(value="", size=14, selectable=True)
    back_to_list_button = ft.IconButton(
        icon="arrow_back",
        width= 50, height= 50,
        tooltip="목록으로 돌아가기"
        # on_click은 핸들러 정의 후에 설정
    )
    # [신규] 메모 뷰를 감싸는 컨테이너
    memo_view_container = ft.Container(
        content=ft.Column(
            controls=[back_to_list_button, memo_display_text],
            scroll=ft.ScrollMode.AUTO
        ),
        padding=ft.padding.all(20), 
        expand=True, 
        alignment=ft.alignment.top_left
    )

    # 3. [신규] 뷰 스위처 (메인 컨텐츠 영역이 됨)
    #    처음에는 'list_view_container'를 보여줍니다.
    main_switch = ft.AnimatedSwitcher(
        content=list_view_container,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
        reverse_duration=200,
        expand=True
    )
    
    # --- [신규] 뷰 전환 핸들러 ---
    
    # [신규] '뒤로가기' 버튼이 호출할 함수
    def main_show_list(e):
        """'메모 뷰'에서 '목록 뷰'로 전환합니다."""
        main_switch.content = list_view_container
        main_switch.update()
    
    # [신규] '뒤로가기' 버튼에 함수 연결
    back_to_list_button.on_click = main_show_list

    # --- 👇 [수정] 여기가 사용자님이 요청하신 'main_clean' 제어 함수입니다 ---
    def main_clean(e, item_data):
        """
        '메모' 버튼 클릭 시 호출됩니다.
        AnimatedSwitcher의 내용을 '메모 뷰'로 전환하고 메모 내용을 채웁니다.
        """
        # 1. 'item_data' 딕셔너리에서 'Memo' 값을 가져옵니다.
        memo_text = item_data.get('Memo')
        
        # 2. '메모 뷰'의 텍스트 컨트롤(memo_display_text) 값을 설정합니다.
        if not memo_text: # memo_val is None or ""
            memo_display_text.value = "저장된 메모가 없습니다."
        else:
            memo_display_text.value = memo_text
        
        # 3. (핵심) AnimatedSwitcher의 내용을 'memo_view_container'로 변경합니다.
        main_switch.content = memo_view_container
        main_switch.update() # 화면 전환
    # --- [수정 끝] ---

    # --- [UI 업데이트 함수] ---
    def update_ui_display():
        
        todo_list.controls.clear()

        total_items = len(all_items_data)
        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
        if total_items == 0:
            total_pages = 1 
            
        if page.current_page > total_pages:
            page.current_page = total_pages
        
        start_index = (page.current_page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        
        items_to_display = all_items_data[start_index:end_index]

        pageNum.value = f"{page.current_page}/{total_pages}"

        # [수정] for item in items_to_display: -> idx, item 추적
        for idx, item in enumerate(items_to_display):
            actual_idx = start_index + idx
            
            title_text = item.get('Title', '')
            due_val = item.get('Due', None)
            memo_val = item.get('Memo')
            link_val = item.get('Link')
            status = item.get('Status', None)
            pre_link = Todo_def.url_mention(link_val)

            # (사용자님의 status 핸들러 - 그대로 유지)
            def create_status_handler(item_idx, dic_value):
                def on_status_select(e):
                    selected_status = e.control.text
                    all_items_data[item_idx]['Status'] = selected_status
                    print(f"항목 {item_idx}의 상태를 {selected_status}로 변경")
                    print(f"딕셔너리 vlaue = {dic_value}") 
                    update_ui_display()
                return on_status_select

            status_display = status if status else "▢"
            
            status_popup = ft.PopupMenuButton(
                content=ft.Text(
                    value=status_display,
                    size=16,
                    weight="w500"
                ),
                items=[
                    ft.PopupMenuItem(text="O", on_click=create_status_handler(actual_idx,1)),
                    ft.PopupMenuItem(text="△", on_click=create_status_handler(actual_idx,2)),
                    ft.PopupMenuItem(text="X", on_click=create_status_handler(actual_idx,3)),
                ], tooltip= 'complete'
            )
            
            # --- 👇 [수정] 'on_click'이 'main_clean'을 호출하도록 변경 ---
            # [삭제] def main_clean(e): (여기 있던 빈 함수 삭제)

            memo_button = ft.IconButton(
                content = ft.Image(src = 'memo.png', width = 12, height = 12),
                opacity=1.0 if memo_val else 0.0,
                tooltip="메모 보기",
                # 람다를 사용해 현재 'item' 딕셔너리를 'main_clean' 함수로 전달
                on_click=lambda e, item_ref=item: main_clean(e, item_ref),
                width=30,
                height=30
            )
            # --- [수정 끝] ---
            
            title_row = ft.Row(
                controls=[
                    status_popup,
                    ft.Text(
                        value=title_text, 
                        size=16, 
                        weight="w500"
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
                color="grey_700",
                opacity=1.0 if due_val else 0.0 
            )

            icon_row_contents = ft.Row(
                controls=[
                    ft.Image(
                        src=pre_link.get('favicon_url') if link_val else None,
                        width = 12, height = 12,
                        opacity=1.0 if link_val else 0.0,
                        padding=ft.padding.only(top=2)
                    ),
                    ft.Text(
                        pre_link.get('title') if link_val else None,
                        size=12,
                        weight=ft.FontWeight.W_500
                    )
                ],
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
            icon_row_controls = ft.Container(
                content=icon_row_contents,
                on_click=lambda _, url=pre_link.get('url'): page.launch_url(url) if url else None,
                
                tooltip=f"링크 열기: {pre_link.get('url')}" if link_val else None,
                padding=0 # 불필요한 여백 제거
            )

            new_item_controls = [
                title_row,  due_text_control, icon_row_controls  
            ]
            
            new_item = ft.Container(
                content=ft.Column(controls=new_item_controls, spacing=1, tight=True),
                padding=ft.padding.only(left=10, top=12, right=10, bottom=12),
                bgcolor='#F5F5F5',
                border_radius=5,
                border=ft.border.all(1, '#E0E0E0')
            )
            
            todo_list.controls.append(new_item)

        # [수정] 뷰가 전환되었을 수도 있으니, 목록 뷰일 때만 page.update()
        if main_switch.content == list_view_container:
            page.update()
        else:
            print("메모 뷰가 활성 중이므로, 목록 UI는 백그라운드에서 갱신됨.")
            
        print(f"UI 업데이트 완료. 현재 {page.current_page}/{total_pages} 페이지 표시.")

    def check_queue(queue_to_check: multiprocessing.Queue):
        while True:
            try:
                data = queue_to_check.get(timeout=0.5) 
                
                all_items_data.append(data)
                
                total_items = len(all_items_data)
                page.current_page = (total_items - 1) // ITEMS_PER_PAGE + 1
                
                update_ui_display()
                print(f"항목 추가. {page.current_page}페이지로 이동.")
                
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Queue 확인 중 오류: {e}")
                time.sleep(0.5)

    def on_page_left(e):
        if page.current_page > 1:
            page.current_page -= 1
            update_ui_display() 

    def on_page_right(e):
        total_items = len(all_items_data)
        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1
        if total_items == 0: total_pages = 1
            
        if page.current_page < total_pages:
            page.current_page += 1
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

    page.title = 'PySchedule'
    page.window.width = 585
    page.window.height = 365
    page.window.resizable = False
    page.window.maximizable = False
    page.padding = 0
    page.bgcolor = '#FFFFFF'
    page.add_window_process = None
    pre_toDay = datetime.date.today()
    
    pageBtn_L = ft.IconButton(
        content=ft.Image(src='Left.png', width=15, height=15),
        tooltip='Left', width=25, height=25,
        on_click=on_page_left 
    )
    pageNum = ft.Text(value='1/1', size=10, weight=ft.FontWeight.W_500)
    pageBtn_R = ft.IconButton(
        content=ft.Image(src='Right.png', width=15, height=15),
        tooltip='Right', width=25, height=25,
        on_click=on_page_right 
    )
    
    sidebar = ft.Container(
        width=90, height=450, bgcolor='#D9D9D9',
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text(value=pre_toDay.strftime("%m."), size=20, weight=ft.FontWeight.W_500, color='#000000'),
                ft.Text(value=pre_toDay.strftime("%d"), size=25, weight=ft.FontWeight.W_500, color='#000000'),
                ft.Container(height=20),
                ft.IconButton(
                    content=ft.Image(src='Add.png', width=25, height=25), 
                    on_click=open_add_window, tooltip='add'
                ),
                ft.Container(height=15),
                ft.IconButton(
                    content=ft.Image(src='Canlender.png', width=25, height=25), 
                    tooltip='calender'
                ),
                ft.Container(height=15),
                ft.IconButton(content = ft.Image(src = 'edit.png', width = 20, height = 20), tooltip = 'edit'),
                ft.Container(expand=True),
                ft.Row(
                    controls=[ pageBtn_L, pageNum, pageBtn_R ],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=5
                ),
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0
        )
    )

    # [수정] main_content가 이제 'main_switch'를 가리킵니다.
    # (todo_list, list_view_container 등은 위에서 이미 정의됨)
    layout = ft.Row(controls=[sidebar, main_switch], spacing=0, expand=True)
    page.add(layout)
    
    update_ui_display()
    
    queue_thread = threading.Thread(target=check_queue, args=(main_queue,), daemon=True)
    queue_thread.start()


if __name__ == "__main__":
    data_queue = multiprocessing.Queue()
    
    ft.app(target=lambda p: main(p, data_queue))