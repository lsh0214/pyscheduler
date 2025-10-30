import flet as ft
from datetime import datetime, timedelta
import json
import os


class SchedulerBackend:
    """스케줄러 백엔드 로직"""
    
    def __init__(self, data_file='schedules.json'):
        self.data_file = data_file
        self.schedules = {}
    
    def add_schedule(self, date_str, schedule_data):
        if not schedule_data.get('title'):
            return False
        if date_str not in self.schedules:
            self.schedules[date_str] = []
        if 'completed' not in schedule_data:
            schedule_data['completed'] = False
        self.schedules[date_str].append(schedule_data)
        return True
    
    def get_schedules_by_date(self, date_str):
        return self.schedules.get(date_str, [])
    
    def update_schedule(self, date_str, index, schedule_data):
        if date_str not in self.schedules:
            return False
        if index < 0 or index >= len(self.schedules[date_str]):
            return False
        if not schedule_data.get('title'):
            return False
        self.schedules[date_str][index] = schedule_data
        return True
    
    def delete_schedule(self, date_str, index):
        if date_str not in self.schedules:
            return False
        if index < 0 or index >= len(self.schedules[date_str]):
            return False
        del self.schedules[date_str][index]
        if not self.schedules[date_str]:
            del self.schedules[date_str]
        return True
    
    def toggle_schedule_completion(self, date_str, index):
        if date_str not in self.schedules:
            return False
        if index < 0 or index >= len(self.schedules[date_str]):
            return False
        current = self.schedules[date_str][index].get('completed', False)
        self.schedules[date_str][index]['completed'] = not current
        return True
    
    def get_current_week_schedules(self):
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        
        weekly = {}
        for i in range(7):
            date = monday + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            weekly[date_str] = self.get_schedules_by_date(date_str)
        return weekly
    
    def save_to_file(self, file_path=None):
        try:
            path = file_path or self.data_file
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.schedules, f, indent=4, ensure_ascii=False)
            return True, f"저장 완료"
        except Exception as e:
            return False, f"저장 오류: {str(e)}"
    
    def load_from_file(self, file_path=None):
        try:
            path = file_path or self.data_file
            if not os.path.exists(path):
                return False, "파일이 없습니다"
            with open(path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            for schedules in loaded.values():
                for s in schedules:
                    if 'completed' not in s:
                        s['completed'] = False
            self.schedules = loaded
            return True, "불러오기 완료"
        except Exception as e:
            return False, f"오류: {str(e)}"


def main(page: ft.Page):
    page.title = "Py스케줄러"
    page.window_width = 1100
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # 윈도우 아이콘 설정
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'py.ico')
    print(f"스크립트 경로: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"아이콘 경로 시도 1: {icon_path}")
    print(f"파일 존재 여부: {os.path.exists(icon_path)}")
    
    if os.path.exists(icon_path):
        page.window_icon = icon_path
        print(f"아이콘 설정 완료: {icon_path}")
    elif os.path.exists('py.ico'):
        page.window_icon = 'py.ico'
        print("아이콘 설정 완료: py.ico (상대경로)")
    else:
        print("py.ico 파일을 찾을 수 없습니다!")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
    
    backend = SchedulerBackend()
    backend.load_from_file()
    
    selected_date = [datetime.now()]  # 리스트로 감싸서 참조 가능하게
    
    # 주간 스케줄 컨테이너들
    weekly_columns = []
    
    def show_snackbar(message, color="green"):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()
    
    def update_weekly_view():
        weekly = backend.get_current_week_schedules()
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        
        for i, col in enumerate(weekly_columns):
            date = monday + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            schedules = weekly.get(date_str, [])
            
            # 컬럼 초기화
            col.controls.clear()
            
            # 스케줄 추가
            for schedule in schedules:
                title = schedule.get('title', '')
                completed = schedule.get('completed', False)
                
                schedule_item = ft.Container(
                    content=ft.Text(
                        title,
                        size=11,
                        color="grey600" if completed else "black87",
                        weight=ft.FontWeight.W_400,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    padding=3,
                    on_click=lambda e, s=schedule: show_schedule_detail(s),
                    ink=True,
                )
                col.controls.append(schedule_item)
        
        page.update()
    
    def show_schedule_detail(schedule):
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def toggle_completion(e):
            schedule['completed'] = checkbox.value
            backend.save_to_file()
            update_weekly_view()
            update_schedule_list()
            page.update()
        
        checkbox = ft.Checkbox(
            label="완료됨",
            value=schedule.get('completed', False),
            on_change=toggle_completion
        )
        
        link_widget = ft.Text(f"URL: {schedule.get('link', '없음')}", size=12)
        if schedule.get('link'):
            link_widget = ft.TextButton(
                schedule.get('link'),
                on_click=lambda e: page.launch_url(schedule.get('link'))
            )
        
        dialog = ft.AlertDialog(
            title=ft.Text("스케줄 상세"),
            content=ft.Column([
                ft.Text(f"제목: {schedule.get('title', 'N/A')}", weight=ft.FontWeight.BOLD),
                ft.Text(f"내용: {schedule.get('desc', '없음')}"),
                link_widget,
                checkbox,
            ], tight=True, spacing=10),
            actions=[ft.TextButton("닫기", on_click=close_dialog)],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def update_schedule_list():
        date_str = selected_date[0].strftime('%Y-%m-%d')
        schedules = backend.get_schedules_by_date(date_str)
        
        schedule_list.controls.clear()
        
        for i, schedule in enumerate(schedules):
            title = schedule.get('title', '제목 없음')
            completed = schedule.get('completed', False)
            has_link = bool(schedule.get('link'))
            
            icon = "✓" if completed else "○"
            display_text = f"{icon} {title}"
            if has_link:
                display_text += " 🔗"
            
            item = ft.Container(
                content=ft.Row([
                    ft.Text(
                        display_text,
                        size=14,
                        color="grey600" if completed else "black87",
                    ),
                ], alignment=ft.MainAxisAlignment.START),
                padding=10,
                border=ft.border.all(1, "grey300"),
                border_radius=5,
                data=i,
                on_click=lambda e, idx=i: edit_schedule_dialog(idx),
            )
            schedule_list.controls.append(item)
        
        selected_date_text.value = f"선택된 날짜: {selected_date[0].strftime('%Y-%m-%d')}"
        page.update()
    
    def add_schedule_dialog(e):
        title_field = ft.TextField(label="제목", autofocus=True)
        desc_field = ft.TextField(label="상세 내용", multiline=True, min_lines=3)
        link_field = ft.TextField(label="링크 (선택)")
        completed_checkbox = ft.Checkbox(label="완료됨", value=False)
        
        def save_schedule(e):
            if not title_field.value:
                show_snackbar("제목을 입력하세요", "red")
                return
            
            schedule_data = {
                'title': title_field.value,
                'desc': desc_field.value or '',
                'link': link_field.value or '',
                'completed': completed_checkbox.value
            }
            
            date_str = selected_date[0].strftime('%Y-%m-%d')
            backend.add_schedule(date_str, schedule_data)
            backend.save_to_file()
            
            dialog.open = False
            update_schedule_list()
            update_weekly_view()
            show_snackbar("스케줄 추가 완료")
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("스케줄 추가"),
            content=ft.Column([
                title_field,
                desc_field,
                link_field,
                completed_checkbox,
            ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO, height=300),
            actions=[
                ft.TextButton("취소", on_click=close_dialog),
                ft.TextButton("저장", on_click=save_schedule),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def edit_schedule_dialog(index):
        date_str = selected_date[0].strftime('%Y-%m-%d')
        schedule = backend.get_schedules_by_date(date_str)[index]
        
        title_field = ft.TextField(label="제목", value=schedule.get('title', ''))
        desc_field = ft.TextField(label="상세 내용", value=schedule.get('desc', ''), multiline=True, min_lines=3)
        link_field = ft.TextField(label="링크", value=schedule.get('link', ''))
        completed_checkbox = ft.Checkbox(label="완료됨", value=schedule.get('completed', False))
        
        def save_schedule(e):
            if not title_field.value:
                show_snackbar("제목을 입력하세요", "red")
                return
            
            schedule_data = {
                'title': title_field.value,
                'desc': desc_field.value or '',
                'link': link_field.value or '',
                'completed': completed_checkbox.value
            }
            
            backend.update_schedule(date_str, index, schedule_data)
            backend.save_to_file()
            
            dialog.open = False
            update_schedule_list()
            update_weekly_view()
            show_snackbar("스케줄 수정 완료")
        
        def delete_schedule(e):
            backend.delete_schedule(date_str, index)
            backend.save_to_file()
            dialog.open = False
            update_schedule_list()
            update_weekly_view()
            show_snackbar("스케줄 삭제 완료")
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("스케줄 수정"),
            content=ft.Column([
                title_field,
                desc_field,
                link_field,
                completed_checkbox,
            ], tight=True, spacing=10, scroll=ft.ScrollMode.AUTO, height=300),
            actions=[
                ft.TextButton("삭제", on_click=delete_schedule),
                ft.TextButton("취소", on_click=close_dialog),
                ft.TextButton("저장", on_click=save_schedule),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def on_date_selected(e):
        if e.control.value:
            selected_date[0] = e.control.value
            update_schedule_list()
    
    def go_to_main(e):
        page.views.pop()
        page.update()
    
    def go_to_scheduler(e):
        page.views.append(scheduler_view)
        page.update()
    
    # 메인 페이지
    day_names = ["월", "화", "수", "목", "금", "토", "일"]
    
    weekly_row = ft.Row(spacing=5, alignment=ft.MainAxisAlignment.CENTER)
    
    for day in day_names:
        day_col = ft.Column(
            [
                ft.Container(
                    content=ft.Text(day, size=14, weight=ft.FontWeight.BOLD),
                    alignment=ft.alignment.center,
                    bgcolor="#eceff1",
                    padding=5,
                    border_radius=5,
                    width=130,
                ),
                ft.Container(
                    content=ft.Column([], scroll=ft.ScrollMode.AUTO),
                    width=130,
                    height=200,
                    bgcolor="white",
                    border=ft.border.all(2, "#212121"),
                    border_radius=5,
                    padding=5,
                ),
            ],
            spacing=2,
        )
        weekly_columns.append(day_col.controls[1].content)
        weekly_row.controls.append(day_col)
    
    main_view = ft.View(
        "/",
        [
            ft.Text("파이썬으로 만든 스케줄러", size=28, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Text("이번 주 일정", size=18, weight=ft.FontWeight.BOLD, color="white"),
                bgcolor="#2196f3",
                padding=10,
                border_radius=8,
                alignment=ft.alignment.center,
            ),
            weekly_row,
            ft.Container(
                content=ft.ElevatedButton(
                    "사용자 지정 스케줄",
                    on_click=go_to_scheduler,
                    bgcolor="#2196f3",
                    color="white",
                ),
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=20),
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
    
    # 스케줄러 페이지
    schedule_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, expand=True)
    
    calendar = ft.DatePicker(
        on_change=on_date_selected,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
    )
    page.overlay.append(calendar)
    
    def open_calendar(e):
        calendar.open = True
        calendar.update()
    
    selected_date_text = ft.Text(f"선택된 날짜: {selected_date[0].strftime('%Y-%m-%d')}")
    
    scheduler_view = ft.View(
        "/scheduler",
        [
            ft.Row([
                ft.ElevatedButton("← 뒤로가기", on_click=go_to_main),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(
                content=ft.Column([
                    ft.Text("날짜 선택", size=16, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "📅 캘린더 열기",
                        on_click=open_calendar,
                    ),
                    selected_date_text,
                ]),
                padding=10,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=5,
            ),
            ft.Divider(),
            ft.Text("스케줄 목록", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=schedule_list,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=5,
                padding=10,
                height=300,
            ),
            ft.Row([
                ft.ElevatedButton(
                    "스케줄 추가",
                    on_click=add_schedule_dialog,
                    bgcolor="#2196f3",
                    color="white",
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
        ],
        scroll=ft.ScrollMode.AUTO,
    )
    
    page.views.append(main_view)
    update_weekly_view()
    update_schedule_list()


if __name__ == '__main__':
    ft.app(target=main)