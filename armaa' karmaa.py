import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout


# Database Functions
def create_db():
    """Creates the database and tasks table if they do not exist."""
    conn = sqlite3.connect('karma.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            time TEXT,
            date TEXT,
            repeat_daily INTEGER,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()


def add_task(task, time, date, repeat_daily):
    """Adds a new task to the database."""
    conn = sqlite3.connect('karma.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO tasks (task, time, date, repeat_daily) 
        VALUES (?, ?, ?, ?)
    ''', (task, time, date, repeat_daily))
    conn.commit()
    conn.close()


def view_tasks():
    """Fetches all tasks from the database."""
    conn = sqlite3.connect('karma.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return tasks


def analyze_tasks():
    """Analyzes tasks to determine incomplete tasks and common times."""
    conn = sqlite3.connect('karma.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    rows = c.fetchall()
    conn.close()

    tasks = [row[1] for row in rows]
    status = [row[5] for row in rows]

    status_counts = {s: status.count(s) for s in set(status)}
    incomplete_tasks = [tasks[i] for i, s in enumerate(status) if s == 'Pending']

    times = [row[2] for row in rows if row[5] == 'Pending']
    most_common_time = max(set(times), key=times.count) if times else 'N/A'

    return incomplete_tasks, most_common_time, status_counts


# Kivy UI Class
class KarmaApp(App):
    def build(self):
        create_db()  # Ensure the database is created
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        title = Label(text='कर्म - To-Do List App', font_size=32, bold=True, size_hint_y=None, height=50)
        layout.add_widget(title)

        button_layout = BoxLayout(orientation='horizontal', spacing=10)
        add_task_btn = Button(text='Add Task', on_press=self.show_add_task_popup)
        view_tasks_btn = Button(text='View Tasks', on_press=self.show_view_tasks_popup)
        ai_analysis_btn = Button(text='AI Analysis', on_press=self.show_ai_analysis_popup)

        button_layout.add_widget(add_task_btn)
        button_layout.add_widget(view_tasks_btn)
        button_layout.add_widget(ai_analysis_btn)

        layout.add_widget(button_layout)

        return layout

    def show_add_task_popup(self, instance):
        """Displays a popup for adding a new task."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        content.add_widget(Label(text='Task Name:'))
        task_input = TextInput(size_hint_y=None, height=40)
        content.add_widget(task_input)

        content.add_widget(Label(text='Time (HH:MM):'))
        time_input = TextInput(size_hint_y=None, height=40)
        content.add_widget(time_input)

        content.add_widget(Label(text='Date (YYYY-MM-DD):'))
        date_input = TextInput(size_hint_y=None, height=40)
        content.add_widget(date_input)

        content.add_widget(Label(text='Repeat Daily:'))
        repeat_checkbox = CheckBox(size_hint_y=None, height=40)
        content.add_widget(repeat_checkbox)

        def add_task_on_press(instance):
            """Handles adding a task to the database."""
            task = task_input.text
            time = time_input.text
            date = date_input.text
            repeat_daily = 1 if repeat_checkbox.active else 0
            add_task(task, time, date, repeat_daily)
            popup.dismiss()

        add_button = Button(text='Add Task', on_press=add_task_on_press)
        content.add_widget(add_button)

        popup = Popup(title='Add Task', content=content, size_hint=(0.8, 0.6))
        popup.open()

    def show_view_tasks_popup(self, instance):
        """Displays a popup with the list of tasks."""
        content = ScrollView(size_hint=(1, 1))
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        tasks = view_tasks()
        for task in tasks:
            layout.add_widget(Label(
                text=f"Task: {task[1]}, Time: {task[2]}, Date: {task[3]}, Repeat Daily: {'Yes' if task[4] == 1 else 'No'}, Status: {task[5]}",
                size_hint_y=None, height=40))

        content.add_widget(layout)
        popup = Popup(title='View Tasks', content=content, size_hint=(0.8, 0.8))
        popup.open()

    def show_ai_analysis_popup(self, instance):
        """Displays a popup with the task analysis report."""
        incomplete_task_list, most_common_time, status_counts = analyze_tasks()
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        content.add_widget(Label(text='Analysis Report:', font_size=20))
        content.add_widget(
            Label(text=f"Most Incomplete Tasks: {', '.join(incomplete_task_list) if incomplete_task_list else 'None'}"))
        content.add_widget(Label(text=f"Most Problematic Time: {most_common_time}"))
        content.add_widget(Label(text=f"Status Counts: {status_counts}"))

        popup = Popup(title='Analysis Report', content=content, size_hint=(0.8, 0.8))
        popup.open()


if _name_ == '_main_':
    KarmaApp().run()