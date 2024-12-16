from functools import partial
from os import listdir, path, remove

from CustomMDSlider import CustomMDSlider
from file_functions import write_new_exercise_rest_time
from kivy.core.audio.audio_sdl2 import SoundLoader
from kivy.metrics import sp
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.slider import MDSliderHandle, MDSliderValueLabel
from text_conversion_functions import convert_text_to_seconds, convert_seconds_to_text

from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.scrollview import ScrollView
from kivymd.uix.appbar import (MDTopAppBar, MDTopAppBarLeadingButtonContainer, MDActionTopAppBarButton,
                               MDTopAppBarTitle, MDTopAppBarTrailingButtonContainer)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDButtonIcon
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHelperText,
    MDTextFieldHintText,
    MDTextFieldMaxLengthText
)
from kivy.properties import ListProperty, StringProperty, Clock, NumericProperty
# from kivy.core.window import Window
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer, MDDialogSupportingText,
)

# Window.size = (1080, 2460)

exercise_items = [x.replace('.txt', '') for x in listdir('exercises')]
sound_complete = SoundLoader.load(path.join("sounds", "set_complete_sound.wav"))
sound_rest = SoundLoader.load(path.join("sounds", "rest_complete.wav"))
past_fifthscreen_val = None

Builder.load_string("""

<CustomOneLineIconListItem>
    MDListItemLeadingIcon:
        icon: "star-four-points-small"
    MDListItemSupportingText:
        text: root.text
    MDIconButton:
        icon: "information"
        theme_icon_color: "Custom"
        on_press: app.get_running_app().root.get_screen("Fourth").make_info_popup(root)
    MDButton:
        on_press: 
            # Basically, this gets the previous_screen variable (which is also a screen) of the FourthScreen, which in 
            # turn calls its add_exercise function
            # Yes, this is an abomination. I know that.
            previous_screen_var = app.get_running_app().root.get_screen("Fourth").previous_screen
            app.get_running_app().root.get_screen(previous_screen_var).add_exercise(root)
            app.change_to_screen(previous_screen_var)
        MDButtonIcon:
            icon: "plus"
        MDButtonText:
            text: "Добавить Упражнение"

<PreviousExercises>
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        MDBoxLayout:
            adaptive_height: True
            spacing: "5dp"

            MDIconButton:
                icon: 'arrow-left-bold'
                on_press: app.sm.current = 'Third'

            MDIconButton:   
                icon: 'magnify'

            MDTextField:
                id: search_field
                on_text: root.set_list_md_icons(self.text, True)
                MDTextFieldHintText:
                    text: 'Поиск Упражнения'
        RecycleView:
            id: rv
            key_viewclass: 'viewclass'
            key_size: 'height'

            RecycleBoxLayout:
                padding: dp(10)
                default_size: None, dp(48)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'


<CircularProgressBar>
    canvas.before:
        Color:
            rgba: root.bar_color + [.3]
        Line:
            width: root.bar_width
            ellipse: (self.x, self.y, self.width, self.height, 0, 360)
    canvas.after:
        Color:
            rgb: root.bar_color
        Line:
            width: root.bar_width
            ellipse: (self.x, self.y, self.width, self.height, 0, (360 - self.set_value*3.6))


<ExerciseSetLayout>
<ExerciseSetLayout>
    
    MDCardSwipeLayerBox:
        id: layer_box
        padding: "8dp"
        
        MDIconButton:
            icon: "trash-can"
            pos_hint: {"center_y": .5}
            on_release: app.get_running_app().root.get_screen(root.screen).delete_set(root)

    MDCardSwipeFrontBox:
        id: front_box
    

""")


class YogaApp(MDApp):
    rv_data = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Olive"
        self.theme_cls.accent_palette = "Olivedrab"

    def update_data(self, rv_data_list):
        self.rv_data = [{'text': item} for item in rv_data_list]

    def build(self):
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(FirstScreen(name='First'))
        self.sm.add_widget(SecondScreen(name='Second'))
        self.sm.add_widget(ThirdScreen(name='Third'))
        self.sm.add_widget(FourthScreen(name='Fourth'))
        self.sm.add_widget(FifthScreen(name='Fifth'))
        self.sm.add_widget(SixthScreen(name='Sixth'))
        self.sm.add_widget(SeventhScreen(name='Seventh'))
        #self.sm.add_widget(AutoMode(name="Auto"))

        return self.sm

    def change_to_screen(self, s, *args, **kwargs):
        self.sm.current = s

    def change_to_First(self, info=False, *args):
        self.sm.current = 'First'
        app.sm.current_screen.change_need_to_update(info)

    def change_to_Second(self, template, additional_template_info, *args):
        app.change_to_screen('Second')
        app.get_running_app().root.get_screen('Second').create_widgets(template)

    def change_to_Third(self, *args):
        self.sm.current = 'Third'  # Я не хотел делать это всё так, но пришлось.
        self.get_running_app().root.get_screen('Third').check_for_creations()

    def change_to_Fourth(self, previous_screen, *args):
        self.sm.current = 'Fourth'
        self.get_running_app().root.get_screen('Fourth').set_previous_screen(previous_screen)

    def change_to_Fifth(self, screen, exercise, mode, *args):
        print("changing_to_fifth....")
        print("screen: ", screen)
        self.get_running_app().root.get_screen('Fifth').set_past_screen(screen, exercise, mode)
        self.get_running_app().root.get_screen('Fifth').create_widgets()
        self.sm.current = 'Fifth'

    def change_to_Sixth(self, time, *args):
        self.sm.current = 'Sixth'
        self.sm.current_screen.start(time)

    def change_to_Seventh(self, *args):
        self.sm.current = 'Seventh'

    def change_to_Auto(self, *args):
        self.sm.current = "Auto"
        app.sm.current_screen.create_widgets()


class FirstScreen(MDScreen):
    """
    The first screen the user sees. It is the screen for creating a workout or a workout
    template. It also shows all of your created templates which you can click for the second
    screen to pop up
    """
    total_training_sessions = 0
    total_training_sessions_text = 'Всего занятий йогой: ' + str(total_training_sessions)
    # Это шаблоны тренировок
    templates = {}

    # А это все упражнения
    # exercises = []
    need_to_update = True
    created = False

    def __init__(self, **kwargs):
        """
        Creates all widgets and adds them on the first screen. Creates templates that
        are a button with the text of the name and the exercises of the template.
        It does so by extracting the template name and values from the dictionary 'templates'
        
        :param kwargs:
        """
        super(FirstScreen, self).__init__(**kwargs)
        self.create_widgets()

    def create_widgets(self):
        if self.need_to_update:
            if self.created:
                app.sm.current_screen.clear_widgets()
            self.layout_root = MDScrollView(do_scroll_x=False, do_scroll_y=True, size_hint=(1, 1))
            self.layout_root.md_bg_color = app.theme_cls.backgroundColor
            self.layout = MDBoxLayout(orientation='vertical', size_hint=(1, None), padding='15dp', spacing="15dp",
                                      adaptive_height=True)
            self.layout.bind(minimum_height=self.layout.setter('height'))
            self.lbl1 = MDLabel(text=self.total_training_sessions_text,
                                size_hint=(1, None), height="30dp", adaptive_height=True)
            # pos_hint={"center_x": .6, "center_y": .5})
            # Кнопка, при нажатии которой откроется второй экран
            self.btn_create = MDButton(MDButtonText(text='Создать Шаблон'),
                                       on_press=app.change_to_Third, size_hint=(.8, None), height="30dp")
            # pos_hint={"center_x": .16, "center_y": .5})

            # self.btn_create.bind(on_press= изменить sm.current на второй экран)
            self.lbl2 = MDLabel(text='Шаблоны:', size_hint_y=None, height="30dp", adaptive_height=True)
            # pos_hint={"center_x": .6, "center_y": .5})

            self.layout.add_widget(self.lbl1)
            self.layout.add_widget(self.btn_create)
            self.layout.add_widget(self.lbl2)

            # self.amount_of_templates = 0
            for filename in listdir('templates'):
                with open(path.join('templates', filename), 'r', encoding='utf-8') as file:
                    # self.amount_of_templates += 1
                    template_name = filename.replace('.txt', '')
                    self.template_layout = CustomMDCard(orientation='vertical', size_hint_y=None, padding='10dp',
                                                        adaptive_height=True, template_name=filename)
                    self.lbl_name = MDLabel(text=str(filename.replace('.txt', '')), size_hint_y=None, height=20,
                                            adaptive_height=True)
                    self.template_layout.add_widget(self.lbl_name)
                    k = 0  # Считает кол-во упражнений в шаблоне
                    template_info = file.readlines()
                    try:
                        *all_exercise_info, extra_template_info = template_info
                    except ValueError as error:
                        print("VALUE_ERROR: ", error)
                        continue
                    if extra_template_info.replace("\n", "") in exercise_items:
                        # Это значит что доп инфы нет
                        all_exercise_info.append(extra_template_info)
                        extra_template_info = None
                    while True:
                        exercise_info = []
                        try:
                            exercise_info.append(all_exercise_info.pop(0))
                            exercise_info.append(all_exercise_info.pop(0))
                        except IndexError:
                            break
                        k += 1
                        if not exercise_info:
                            break
                        num_of_exercise, exercise = exercise_info
                        num_of_exercise = str(num_of_exercise.replace("\n", ""))
                        exercise = str(exercise.replace("\n", ""))
                        text_1 = str(k) + " - " + exercise + " x" + num_of_exercise
                        self.template_lbl = MDLabel(text=text_1, size_hint_y=None, height=20, adaptive_height=True)
                        self.template_layout.add_widget(self.template_lbl)

                    self.template_btn = MDButton(MDButtonText(text="Начать тренировку"), size_hint=(1, 1))
                    self.template_btn.bind(on_press=partial(app.change_to_Second, template_name))
                    self.template_layout.add_widget(self.template_btn)
                    self.layout.add_widget(self.template_layout)
                    file.close()

            self.layout_root.add_widget(self.layout)
            self.add_widget(self.layout_root)
            self.need_to_update = False
            self.created = True

    def change_need_to_update(self, info):
        self.need_to_update = info
        self.create_widgets()


class CustomMDCard(MDCard):
    """
        Used for displaying a template in the FirstScreen.
    """

    def __init__(self, template_name, **kwargs):
        super().__init__(**kwargs)
        self.padding = "4dp"
        self.spacing = "4dp"
        self.adaptive_height = True
        self.style = "outlined"
        self.template_name = template_name
        self.root_layout = MDRelativeLayout(size_hint=(1, 1))
        # self.root_layout.bind(minimum_height=self.root_layout.setter('height'))
        self.info_btn = MDIconButton(icon="dots-vertical", pos_hint={"top": 1, "right": 1}, size_hint=(None, None),
                                     size=("40dp", "40dp"))
        self.info_btn.bind(on_press=self.open_menu)
        self.root_layout.add_widget(self.info_btn)
        self.layout = MDBoxLayout(orientation="vertical", spacing="4dp", padding="2dp", adaptive_height=True,
                                  size_hint=(1, 1))
        self.root_layout.add_widget(self.layout)
        self.add_widget(self.root_layout)

    def give_widget_to_layout(self, widget):
        self.layout.add_widget(widget)

    def open_menu(self, instance):
        menu_items = [
            {
                "text": "Удалить шаблон",
                "on_release": lambda x=instance.parent.parent: self.initiate_confirmation(x,
                                                                                          self.template_name
                                                                                          ),
            }
        ]
        MDDropdownMenu(caller=instance, items=menu_items).open()

    def initiate_confirmation(self, layout, template):
        text_item = "Вы уверены, что хотите удалить этот шаблон?"

        self.dialog = MDDialog(
            MDDialogIcon(
                icon="refresh",
            ),
            MDDialogHeadlineText(
                text=text_item
            ),
            MDDivider(),
            MDDialogContentContainer(),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Отмена"),
                    style="text",
                    on_press=self.on_cancel_btn
                ),
                MDButton(
                    MDButtonText(text="Подтвердить"),
                    style="text",
                    on_press=partial(self.confirm, template, layout)
                )
            )
        )
        self.dialog.open()

    def on_cancel_btn(self, instance):
        self.dialog.dismiss()

    def confirm(self, template, layout, instance):
        layout.parent.remove_widget(layout)
        remove(path.join("templates", template))
        self.dialog.dismiss()


class ExerciseSetLayout(MDCardSwipe):
    def __init__(self, num_of_exc, num_of_set, screen, **kwargs):
        super(ExerciseSetLayout, self).__init__(**kwargs)
        self.num_of_exc = num_of_exc
        self.num_of_set = num_of_set
        self.screen = screen


# class MDAutoCheckbox(MDCheckbox):
#    def on_active(self, checkbox, value):
#       super(MDAutoCheckbox, self).on_active()
#        if self.state == "down":
#            update_stats()


class SecondScreen(MDScreen):
    additional_primary_info = []
    event_items = []
    time_text = "Время тренировки: "
    saved_training_time = 0
    current_template = None
    no_additional_info = False
    need_to_change_first_screen = False
    updated = False

    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)
        self.started = False
        self.past_template = None
        self.training_time = 0

    def create_widgets(self, template):
        print("creating widgets for screen 2")
        for event in self.event_items:
            Clock.unschedule(event)
            self.event_items.remove(event)
            del event
            print("found events")
            print(self.event_items)
        self.training_time = 0
        # Это нужно чтобы не создавался второй точно такой же экран
        self.additional_primary_info = []
        if template == self.past_template:
            self.start()
            print("Started")
        else:
            if self.started:
                app.sm.current_screen.clear_widgets()  # Убирает прошлый экран

            self.all_exercise_input_items = []
            self.exercise_input_items = []
            self.nums_of_set = []
            self.started = True
            self.past_template = template
            name = str(template)
            layout_root = MDScrollView(do_scroll_x=False, do_scroll_y=True, size_hint=(1, 1))
            layout_root.md_bg_color = app.theme_cls.backgroundColor
            self.layout = MDBoxLayout(orientation='vertical', size_hint=(1, None), padding='10dp',
                                      spacing="25dp", adaptive_height=True)
            self.layout.bind(minimum_height=self.layout.setter('height'))

            btn_cancel = MDActionTopAppBarButton(icon="arrow-left-bold", size_hint=(None, None),
                                                 size=('60dp', '60dp'))
            btn_cancel.bind(on_press=self.exit_screen)

            self.btn_rest = MDActionTopAppBarButton(icon="clock-outline", size_hint=(None, None),
                                                    size=('60dp', '60dp'))
            self.btn_auto = MDActionTopAppBarButton(icon="auto-mode", size_hint=(None, None),
                                                    size=('120dp', '60dp'))

            top_app_bar = MDTopAppBar(MDTopAppBarLeadingButtonContainer(btn_cancel), MDTopAppBarTitle(
                text=name),
                                      MDTopAppBarTrailingButtonContainer(self.btn_rest, self.btn_auto),
                                      type="small", pos_hint={"center_x": .5, "top": 1})

            self.btn_rest.bind(on_press=partial(app.change_to_Fifth, "Second", None, True))
            #self.btn_auto.bind(on_release=self.engage_auto_mode)
            self.layout.add_widget(top_app_bar)

            # Далее с генеалогическим деревом данного класса начинается полный пиздец. Это не шутка.
            self.parent_layout = MDBoxLayout(orientation='vertical', size_hint=(1, None), adaptive_height=True)

            self.time_lbl = MDLabel(text="Время тренировки: ", size_hint=(1, None), height="40dp")
            self.layout.add_widget(self.time_lbl)
            self.layout.add_widget(self.parent_layout)

            file_name = str("{}.txt".format(template))
            file = open(path.join('templates', file_name), 'r', encoding='utf-8')
            template_info = file.readlines()
            file.close()

            *self.all_exercise_info, self.extra_template_info = template_info
            if self.extra_template_info.replace("\n", "") in exercise_items:
                # Это значит что доп инфы нет
                self.all_exercise_info.append(self.extra_template_info)
                extra_template_info = None
            print("Additional info: ", self.extra_template_info)

            self.num_of_exercise = 0
            self.current_template = file_name
            while True:
                some_layout = MDBoxLayout(orientation='vertical', size_hint=(1, None), padding='4dp',
                                          adaptive_height=True)
                exercise_info_from_template = []
                try:
                    exercise_info_from_template.append(self.all_exercise_info.pop(0))
                    exercise_info_from_template.append(self.all_exercise_info.pop(0))
                except IndexError:
                    break
                self.num_of_exercise += 1
                self.all_exercise_input_items.append([])

                self.num_of_set, self.exercise = exercise_info_from_template
                self.num_of_set = int(self.num_of_set.replace('\n', ''))  # кол-во упражнений
                self.exercise = self.exercise.replace('\n', '')  # само упражнение
                exercise_file_name = str(f'{self.exercise}.txt')  # название файла упражнения
                self.nums_of_set.append(self.num_of_set)

                # файл упражнения
                exercise_file = open(path.join('exercises', exercise_file_name), 'r', encoding='utf-8')
                self.exercise_info = exercise_file.readlines()  # вся информация упражнения
                type_of_exercise = self.exercise_info[3]  # тип упражнения (время или повторы)
                type_of_exercise = type_of_exercise.replace("\n", "")
                self.rest_time = self.exercise_info[1]  # время отдыха у упражнения
                exercise_file.close()

                upper_exc_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height='20dp')
                exercise_name_lbl = MDLabel(text=self.exercise, size_hint_y=None, height="30dp", adaptive_height=True)
                upper_exc_layout.add_widget(exercise_name_lbl)
                upper_exc_layout.ids["exc_name_lbl"] = exercise_name_lbl
                btn_exercise_settings = MDIconButton(icon='dots-vertical', size_hint=(None, None),
                                                     size=('30dp', '30dp'))  # , style='outlined'
                btn_exercise_settings.bind(on_press=partial(self.open_settings, self.exercise, some_layout))
                upper_exc_layout.add_widget(btn_exercise_settings)
                some_layout.add_widget(upper_exc_layout)
                some_layout.ids["upper_layout"] = upper_exc_layout
                exercise_type_lbl = MDLabel(text=type_of_exercise, size_hint_y=None, height="30dp",
                                            adaptive_height=True)
                some_layout.add_widget(exercise_type_lbl)

                holder = MDBoxLayout(orientation='vertical', size_hint=(1, None), adaptive_height=True)
                some_layout.add_widget(holder)
                some_layout.ids["holder"] = holder

                for i in range(self.num_of_set):
                    print("i: ", i)
                    self.add_set(number_of_set=i, num_of_exercise=self.num_of_exercise, set_layout=holder,
                                 type_of_exc=type_of_exercise, rest_time=self.rest_time)

                # self.all_exercise_input_items.append(self.exercise_input_items)
                # self.exercise_input_items =[]

                add_set_btn = AddSetMDButton(pos_hint={"center_x": .5}, num_of_exc=self.num_of_exercise,
                                             num_of_set=self.num_of_set, type_of_exc=type_of_exercise,
                                             r_time=self.rest_time)
                print("self.num_of_exercise: ", self.num_of_exercise)
                # add_set_btn.bind(on_press=partial(self.add_set_btn_command, num_of_exercise=self.num_of_exercise))

                some_layout.add_widget(add_set_btn)
                some_layout.ids["add_set_btn"] = add_set_btn
                self.parent_layout.add_widget(some_layout)

            add_exercise_btn = MDButton(MDButtonText(text='Добавить Упражнение'),
                                        size_hint=(1, None), pos_hint={"center_x": 0.5})
            add_exercise_btn.bind(on_press=partial(app.change_to_Fourth, "Second"))
            self.layout.add_widget(add_exercise_btn)

            end_of_workout_btn = MDButton(MDButtonText(text='Закончить Тренировку'),
                                          size_hint=(1, None), pos_hint={"center_x": 0.5})
            end_of_workout_btn.bind(on_press=self.stop_training)
            self.layout.add_widget(end_of_workout_btn)
            layout_root.add_widget(self.layout)
            self.add_widget(layout_root)
            self.start()

    def start(self, *args):
        self.training_time = 0
        event = Clock.schedule_interval(self.update_time_text, 1.0)
        print("event initialized")
        self.event_items.append(event)

    def update_time_text(self, dt):
        self.training_time += dt
        self.time_lbl.text = "Время тренировки: " + convert_seconds_to_text(int(self.training_time))

    def add_set_btn_command(self, num_of_exercise, num_of_set, layout, instance, type_of_exc, rest_time):
        self.updated = True
        instance.num_of_set += 1
        self.nums_of_set[num_of_exercise - 1] += 1
        print("self.nums_of_set: ", self.nums_of_set)
        self.add_set(num_of_set, num_of_exercise, layout, type_of_exc, rest_time)

    def add_set(self, number_of_set, num_of_exercise, set_layout, type_of_exc, rest_time, *args):
        # set_layout being holder
        print("number: ", number_of_set)
        exercise_set_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None),
                                          adaptive_height=True, spacing="15dp", padding="5dp")
        exercise_text = str(number_of_set + 1) + "."
        exercise_num_lbl = MDLabel(text=exercise_text, size_hint=(None, None), height="40dp",
                                   adaptive_height=True)
        exercise_set_layout.add_widget(exercise_num_lbl)
        exercise_set_layout.ids["exercise_num_lbl"] = exercise_num_lbl
        exercise_input = My_MDTextField(size_hint_y=None, height="40dp", exc_info=self.exercise_info,
                                        n_of_exc=num_of_exercise, n_of_set=(number_of_set + 1),
                                        add_info=self.extra_template_info, type_of_exc=type_of_exc)
        self.all_exercise_input_items[num_of_exercise - 1].append(exercise_input)

        print("all_exercise_input_items: ", self.all_exercise_input_items)
        self.exercise_input_items.append(exercise_input)
        # exercise_input.bind(on_text=partial(exercise_input.on_text, exercise_info_from_template ))
        exercise_set_layout.add_widget(exercise_input)
        exercise_set_layout.ids["time_input"] = exercise_input
        exc_complete_checkbox = CustomMDCheckbox(size_hint=(None, None), size=('40dp', '40dp'),
                                                 adaptive_height=True, r_time=rest_time)
        # exc_complete_checkbox.bind(on_state=self.on_checkbox_state)
        exercise_set_layout.add_widget(exc_complete_checkbox)
        print("num_of_exercise: ", num_of_exercise)
        exercise_set_layout_holder = ExerciseSetLayout(size_hint_y=None, adaptive_height=True,
                                                       num_of_exc=num_of_exercise, num_of_set=number_of_set,
                                                       screen="Second")
        exercise_set_layout_holder.ids["front_box"].add_widget(exercise_set_layout)
        exercise_set_layout_holder.ids["front_box"].ids["exercise_set_layout"] = exercise_set_layout
        set_layout.add_widget(exercise_set_layout_holder)

    def delete_set(self, layout, *args):
        """
        :param layout: the ExerciseSetLayout.
        """
        self.updated = True
        print("deleting set..")
        child_var = self.parent_layout.children[:]  # child_var are all some_layouts
        child_var.reverse()
        holder = layout.parent  # The needed holder but faster
        some_layout = holder.parent  # The some_layout that is the parent of the holder
        some_layout.ids["add_set_btn"].num_of_set -= 1
        # holder = child_var[layout.num_of_exc - 1].ids["holder"]   The needed holder
        holder.remove_widget(layout)  # holder.children.reversed()[layout.num_of_set]. This was a line of code
        # that was in the parentheses of remove_widget(). Why is it so complicated????
        self.nums_of_set[layout.num_of_exc - 1] -= 1

        holder_children = holder.children[:]
        holder_children.reverse()
        for child in holder_children:  # child = exercise_set_layout_holder
            if child.num_of_set > layout.num_of_set:
                child.num_of_set -= 1
                child_var_2 = child.ids["front_box"].ids["exercise_set_layout"]
                child_var_2.ids["exercise_num_lbl"].text = str(child.num_of_set + 1)
                child_var_2.ids["time_input"].number_of_set -= 1
        del self.all_exercise_input_items[layout.num_of_exc - 1][layout.num_of_set]

    def on_custom_checkbox_active(self, rest_time):
        rest_time = int(rest_time.replace("\n", ""))
        global past_fifthscreen_val
        past_fifthscreen_val = 'Second'
        app.change_to_Sixth(rest_time)

    def add_exercise(self, widget, *args):
        self.num_of_exercise += 1
        self.all_exercise_input_items.append([])
        exc_name = str(widget.text)
        some_layout = MDBoxLayout(orientation='vertical', size_hint=(1, None), padding='4dp',
                                  adaptive_height=True)
        self.nums_of_set.append(1)
        self.additional_primary_info.append(exc_name)

        # файл упражнения
        exercise_file = open(path.join('exercises', (exc_name + ".txt")), 'r', encoding='utf-8')
        self.exercise_info = exercise_file.readlines()  # вся информация упражнения
        type_of_exercise = self.exercise_info[3]  # тип упражнения (время или повторы)
        type_of_exercise = type_of_exercise.replace("\n", "")
        self.rest_time = self.exercise_info[1]  # время отдыха у упражнения
        exercise_file.close()

        upper_exc_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None), height='20dp')
        exercise_name_lbl = MDLabel(text=self.exercise, size_hint_y=None, height="30dp", adaptive_height=True)
        upper_exc_layout.add_widget(exercise_name_lbl)
        upper_exc_layout.ids["exc_name_lbl"] = exercise_name_lbl
        btn_exercise_settings = MDIconButton(icon='dots-vertical', size_hint=(None, None),
                                             size=('30dp', '30dp'))  # , style='outlined'
        btn_exercise_settings.bind(on_press=self.open_settings)
        upper_exc_layout.add_widget(btn_exercise_settings)
        some_layout.add_widget(upper_exc_layout)
        some_layout.ids["upper_layout"] = upper_exc_layout
        exercise_type_lbl = MDLabel(text=type_of_exercise, size_hint_y=None, height="30dp",
                                    adaptive_height=True)
        some_layout.add_widget(exercise_type_lbl)

        holder = MDBoxLayout(orientation='vertical', size_hint=(1, None), adaptive_height=True)
        some_layout.add_widget(holder)
        some_layout.ids["holder"] = holder

        self.add_set(number_of_set=0, num_of_exercise=self.num_of_exercise, set_layout=holder,
                     type_of_exc=type_of_exercise, rest_time=self.rest_time)

        add_set_btn = AddSetMDButton(pos_hint={"center_x": .5}, num_of_exc=self.num_of_exercise,
                                     num_of_set=1, type_of_exc=type_of_exercise, r_time=self.rest_time)
        print("self.num_of_exercise: ", self.num_of_exercise)

        some_layout.add_widget(add_set_btn)
        some_layout.ids["add_set_btn"] = add_set_btn
        self.parent_layout.add_widget(some_layout)
        self.updated = True

    def open_settings(self, exercise, layout, initiator):
        menu_items = [
            {"text": "Изменить время отдыха",
             "on_release": lambda y=exercise: self.change_screen(y)
             },
            {"text": "Удалить упражнение",
             "on_release": lambda x=layout: self.delete_exc(x)
             }
        ]

        MDDropdownMenu(caller=initiator, items=menu_items, position="bottom"
                       ).open()

    def delete_exc(self, layout):
        self.updated = True
        print("deleting exercise..................")
        del self.nums_of_set[layout.ids["add_set_btn"].num_of_exc - 1]
        self.num_of_exercise -= 1
        self.parent_layout.remove_widget(layout)
        print("self.num_of_exercise: ", self.num_of_exercise)
        print("self.nums_of_set: ", self.nums_of_set)

    def change_screen(self, exercise):
        app.change_to_Fifth("Second", exercise, False)

    def stop_training(self, *args):
        for event_item in self.event_items:
            print("Found_events_after_training")
            Clock.unschedule(event_item)
            self.event_items.remove(event_item)  # I think this is actually not needed since there is del event_item
            del event_item

        self.saved_training_time = self.training_time
        self.training_time = 0
        if self.updated:
            self.confirm_update()

    def update_template_info(self, primary=False, additional=False, *args):
        """
        Will update template info
        :param primary: the need to update primary info. False by default.
        :param additional: the need to update additional info. False by default.
        """
        all_additional_info = []
        all_primary_info = []
        num_of_exercise = 0
        children = self.parent_layout.children
        children.reverse()
        with open(path.join("templates", self.current_template), "r", encoding="utf-8") as file:
            file_info = file.readlines()
            *old_primary_info, old_additional_info = file_info
            if old_additional_info in exercise_items:
                old_primary_info.append(old_additional_info)

        for child in children:  # child in this case being some_layout
            num_of_set = 0
            num_of_exercise += 1
            upper_layout = child.ids["upper_layout"]
            name_of_exc = upper_layout.ids["exc_name_lbl"].text
            holder = child.ids["holder"]
            children_var_1 = holder.children
            children_var_1.reverse()
            for child_var in children_var_1:  # child_var being the exercise_set_layout
                try:
                    num_of_set += 1
                    print("num_of_set: ", num_of_set)
                    exercise_set_layout = child_var.ids["front_box"].ids["exercise_set_layout"]
                    type_of_exc = exercise_set_layout.ids["time_input"].validator
                    time = exercise_set_layout.ids["time_input"].text  # Может быть и повторения, а не время
                    if type_of_exc == "time":
                        time = convert_text_to_seconds(time)
                    else:
                        print("type_of_exc: ", type_of_exc)
                    # additional_info = str(num_of_exercise) + str(num_of_set) + str(time) + ", "
                    all_additional_info.append(str(num_of_exercise))
                    all_additional_info.append(str(num_of_set))
                    all_additional_info.append(str(time))
                except IndexError:  # Если нет time
                    print("time=False")
                    continue
            all_primary_info.append(str(num_of_set) + "\n")
            all_primary_info.append(name_of_exc + "\n")

            if primary or additional:
                with open(path.join("templates", self.current_template), "w", encoding="utf-8") as file:
                    # I'm 100% sure that there is a better way to do this.
                    if primary and additional:
                        for info_item in all_primary_info:
                            file.write(info_item)
                        for info_item in all_additional_info:
                            file.write(info_item + ", ")
                    elif primary:
                        for info_item in all_primary_info:
                            file.write(info_item)
                        for info_item in old_additional_info:
                            file.write(info_item + ", ")
                    elif additional:
                        for info_item in old_primary_info:
                            file.write(info_item)
                        for info_item in all_additional_info:
                            file.write(info_item + ", ")
        app.change_to_First(True)
        self.confirm_dialog.dismiss()
        self.past_template = None

    def confirm_update(self):
        self.confirm_dialog = MDDialog(
            MDDialogIcon(
                icon="refresh",
            ),
            MDDialogHeadlineText(
                text="Обновить данные шаблона?"
            ),
            MDDivider(),
            MDDialogContentContainer(

                MDButton(
                    MDButtonText(text="Ничего не обновлять"),
                    style="text",
                    on_press=self.on_dont_update_btn
                ),
                MDButton(
                    MDButtonText(text="Обновить шаблон и величины"),
                    style="filled",
                    on_press=partial(self.update_template_info, True, True)
                ),
                MDButton(
                    MDButtonText(text="Обновить величины"),
                    style="filled",
                    on_press=partial(self.update_template_info, False, True)
                ),
                orientation="vertical"
            )
        )
        self.confirm_dialog.open()

    def exit_screen(self, *args):
        app.change_to_First(self.need_to_change_first_screen)
        if self.updated:
            self.past_template = None

    def on_dont_update_btn(self, *args):
        self.past_template = None
        app.change_to_First()
        self.confirm_dialog.dismiss()

    # TODO: Найти нормальное название для авторежима.
    def engage_auto_mode(self, initiator):
        self.dialog = MDDialog(
            MDDialogIcon(icon='auto-mode'),
            MDDialogHeadlineText(text="Запустить"),
            MDDialogSupportingText(text="placeholder_name - это"),
            # MDDialogContentContainer(
            #    MDBoxLayout(
            #       MDCheckbox(on_value=self.on_auto_checkbox_active),
            #        MDLabel(text="Больше не показывать"),
            #        orientation="horizontal", padding="4dp", spacing="4dp"
            #    ),
            # ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Начать"),
                    on_release=self.start_auto_mode),
                MDButton(
                    MDButtonText(text="Отмена"),
                    on_press=self.on_dismiss_btn_press),
                spacing="8dp"),
            size_hint=(None, None), size=(self.width * .5, self.height * .8))
        self.dialog.open()

    def on_dismiss_btn_press(self, *args):
        self.dialog.dismiss()

    def on_auto_checkbox_active(self, checkbox, value):
        print("Checkbox ", checkbox, " is ", checkbox.state, " with value ", value)

    def start_auto_mode(self, *args):
        #app.change_to_Auto()
        pass


class AddSetMDButton(MDButton):
    def __init__(self, num_of_exc, num_of_set, type_of_exc, r_time, **kwargs):
        super(AddSetMDButton, self).__init__(**kwargs)
        self.add_widget(MDButtonIcon(icon="plus"))
        self.add_widget(MDButtonText(text="Добавить подход"))
        self.num_of_exc = num_of_exc
        self.num_of_set = num_of_set
        self.type_of_exc = type_of_exc
        self.rest_time = r_time

    def on_press(self, *args):
        layout = self.parent.ids["holder"]
        # С каждым днём мы всё больше отдаляемся от Бога.
        layout.parent.parent.parent.parent.parent.add_set_btn_command(num_of_exercise=self.num_of_exc,
                                                                      num_of_set=self.num_of_set, layout=layout,
                                                                      instance=self, type_of_exc=self.type_of_exc,
                                                                      rest_time=self.rest_time)


class CustomMDCheckbox(MDCheckbox):
    def __init__(self, r_time, **kwargs):
        super().__init__(**kwargs)
        self.exercise_rest_time = r_time

    def on_state(self, *args):
        super(CustomMDCheckbox, self).on_state(*args)
        initiator, state = args
        parent_exercise_set_layout = initiator.parent.ids["time_input"]

        if state == "down":
            with parent_exercise_set_layout.canvas:
                Color(0, 1, .1, .1)
                Rectangle(pos=parent_exercise_set_layout.pos, size=parent_exercise_set_layout.size,
                          radius=parent_exercise_set_layout.radius, group=u"0")
            sound_complete.play()
            app.get_running_app().root.get_screen("Second").on_custom_checkbox_active(
                rest_time=self.exercise_rest_time)
        else:
            parent_exercise_set_layout.canvas.remove_group(u"0")


class My_MDTextField(MDTextField):
    def __init__(self, add_info, exc_info, n_of_exc, n_of_set, type_of_exc, **kwargs):
        """
        Will initialize the textfield.
        :param exc_info: the information of the current exercise. Stored in the
        exercises folder
        :param n_of_exc: the number of the exercise in order
        :param n_of_set: the number of the current set of the exercise
        :param kwargs: stuff for initializing
        """
        super(My_MDTextField, self).__init__(**kwargs)
        self.multiline = False
        s_name, time_of_rest, muscles, type_of_exercise, image, *instructions = exc_info
        self.additional_info = None
        self.type_of_exc = type_of_exc

        if str(type_of_exercise.replace("\n", "")) == "Время":
            self.validator = "time"
            self.add_widget(MDTextFieldHintText(text="Время (Формат:  00:00)"))
        else:
            self.add_widget(MDTextFieldHintText(text="Количество повторений"))

        # These variables will be used in update_extra_template_info of the SecondScreen
        self.number_of_exercise = n_of_exc
        self.number_of_set = n_of_set
        try:
            self.all_additional_info = add_info.split(", ")
        except AttributeError:
            # When there is no additional_info
            self.all_additional_info = None
        self.text_info = self.text
        if self.all_additional_info:
            print("self.all_additional_info exists: ", self.all_additional_info)
            # When there was no exception above
            self.text = self.text_from_additional_info()
            self.text_info = self.text

    def on_text(self, instance, text_var):
        self.text_info = text_var

    def text_from_additional_info(self):
        """
            Makes a text_value from additional info for the MDTextField. Is activated ONLY if there is
            actually additional info present
        :return:
        """
        text_value = ""
        self.additional_info = []
        self.additional_info.append(str(self.number_of_exercise))
        self.additional_info.append(str(self.number_of_set))

        starting_index = -3
        while True:
            starting_index += 3
            try:
                num_of_exc = self.all_additional_info[starting_index]
                num_of_set = self.all_additional_info[starting_index + 1]
            except IndexError:
                break
            comparison_list = []
            comparison_list.append(str(num_of_exc))
            comparison_list.append(str(num_of_set))
            if self.additional_info == comparison_list:
                time_val = self.all_additional_info[starting_index + 2]
                if self.type_of_exc == "Время":
                    # I wrote replace() here for a reason.
                    text_value = convert_seconds_to_text(int(str(time_val).replace(",", "")))
                else:
                    text_value = time_val
                break
        return text_value


class ThirdScreen(MDScreen):
    """
    In this window the user will create their own training regimen. The first widget will be
    the TextInput. The second widget is a button that will redirect the person to the Fourth Screen.
    When a button is pressed and the exercise is added, there will appear below the add exercise
    button a new exercise.
    The next widget is the exercise name.
    Then the button to add a new 'set' of the exercise
    Then below it is the type of exercise (kinda important)
    Then each set. A set contains its number and a TextInput with the time of the set.
    """

    def __init__(self, **kwargs):
        super(ThirdScreen, self).__init__(**kwargs)
        self.created = False

    def check_for_creations(self, *args):
        """
        При перемене sm.current с помощью кнопок других экранов будет использована функция
        create_widgets. Но если эта функция уже использована, то будет создан второй точно
        такой же экран (если нет изменений), наложенный на первый. Это плохо для оптимизации
        (очевидно). Поэтому в конце создания элементов экрана self.check = True. Теперь при
        каждом нажатии кнопки, меняющей тот экран на этот, будет проведена проверка. Если
        экран не делался, то будут созданы элементы экрана, а если делался, то ничего не
        произойдёт.
        """
        if self.created:
            pass
        else:
            self.create_widgets()

    def create_widgets(self):
        self.num_of_exercise = 0
        self.nums_of_set = []

        self.layout_root = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint=(1, 1))
        self.layout = MDBoxLayout(orientation='vertical', size_hint=(1, None), padding='10dp',
                                  spacing="15dp", adaptive_height=True)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        exit_btn = MDIconButton(icon="arrow-left-bold", size_hint=(None, None),
                                size=('50dp', '50dp'), pos_hint={"center_y": 0.4})
        exit_btn.bind(on_press=partial(app.change_to_First, False))

        self.name_input = MDTextField(MDTextFieldHintText(text="Название тренировки"),
                                      MDTextFieldMaxLengthText(max_text_length=20),
                                      MDTextFieldHelperText(text="Ошибка", mode="on_error"),
                                      multiline=False, size_hint=(1, None), height='50dp')

        btn_add_exercise = MDButton(MDButtonIcon(icon="plus"), MDButtonText(text='Добавить упражнение'),
                                    size_hint=(1, None), height="80dp")
        btn_add_exercise.bind(on_press=partial(app.change_to_Fourth, "Third"))

        upper_layout = MDBoxLayout(orientation='horizontal', size_hint=(1, None),
                                   padding='10dp', spacing='10dp', adaptive_height=True)
        upper_layout.add_widget(exit_btn)
        upper_layout.add_widget(self.name_input)
        upper_layout.add_widget(btn_add_exercise)
        self.layout.add_widget(upper_layout)

        self.parent_layout = MDBoxLayout(orientation='vertical', size_hint=(1, None), adaptive_height=True)

        btn_complete_template = MDButton(MDButtonIcon(icon="check"), MDButtonText(
            text="Создать шаблон"), size_hint=(1, None), pos_hint={"center_x": .5, "center_y": .5})
        btn_complete_template.bind(on_press=self.complete_template)

        self.layout.add_widget(self.parent_layout)
        self.layout.add_widget(btn_complete_template)
        self.layout_root.add_widget(self.layout)
        self.add_widget(self.layout_root)

        self.created = True

    def add_exercise(self, widget):
        self.num_of_exercise += 1
        exc_name = widget.text
        exc_file = open(path.join("exercises", (exc_name + ".txt")), "r", encoding='utf-8')
        s_name, rest_time, muscles, exc_type, image, *instructions = exc_file.readlines()

        some_layout = MDBoxLayout(orientation="vertical", size_hint=(1, None),
                                  padding='10dp', spacing='10dp', adaptive_height=True)

        exc_name_lbl = MDLabel(text=exc_name, size_hint=(1, None), height="20dp",
                               pos_hint={"center_x": .5, "center_y": .5}, adaptive_height=True)

        exc_menu_btn = MDIconButton(icon="dots-vertical", size_hint=(None, None),
                                    size=("60dp", "60dp"),
                                    pos_hint={"center_x": .5, "center_y": .5})
        exc_menu_btn.bind(on_press=partial(self.menu_open, layout=some_layout, exercise=exc_name))

        upper_exercise_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, None), padding="5dp",
                                            spacing="5dp", adaptive_height=True)
        upper_exercise_layout.add_widget(exc_name_lbl)
        upper_exercise_layout.add_widget(exc_menu_btn)
        upper_exercise_layout.ids["exc_name_lbl"] = exc_name_lbl
        # upper_exercise_layout.ids["exc_menu_btn"] = exc_menu_btn
        some_layout.add_widget(upper_exercise_layout)
        some_layout.ids["upper_layout"] = upper_exercise_layout

        exc_type_lbl = MDLabel(text=exc_type, size_hint=(.8, None), height="60dp",
                               pos_hint={"center_x": .5, "center_y": .5}, adaptive_height=True)
        some_layout.add_widget(exc_type_lbl)

        holder = MDBoxLayout(orientation="vertical", size_hint=(1, None), padding='10dp',
                             spacing='10dp', adaptive_height=True)

        # self.nums_of_set[self.num_of_exercise-1].append(0)
        self.nums_of_set.append(0)
        self.add_set(layout=holder, type_of_exc=exc_type, num_of_exc=self.num_of_exercise, num_of_set=1)

        some_layout.add_widget(holder)
        some_layout.ids["holder"] = holder

        add_set_btn = AddSetMDButton(num_of_exc=self.num_of_exercise, pos_hint={"center_x": .5, "center_y": .5},
                                     num_of_set=(self.nums_of_set[self.num_of_exercise - 1] + 1), type_of_exc=exc_type,
                                     r_time=rest_time)
        some_layout.add_widget(add_set_btn)
        some_layout.ids["add_set_btn"] = add_set_btn
        self.parent_layout.add_widget(some_layout)

    def add_set_btn_command(self, num_of_set, num_of_exercise, type_of_exc, layout, instance, rest_time):
        instance.num_of_set += 1
        self.add_set(num_of_exercise, layout, type_of_exc, num_of_set)

    def add_set(self, num_of_exc, layout, type_of_exc, num_of_set, *args):
        print("num_of_exc: ", num_of_exc)
        print("num_of_set: ", num_of_set)
        print("self.nums_of_set: ", self.nums_of_set)
        self.nums_of_set[num_of_exc - 1] += 1

        set_layout_holder = ExerciseSetLayout(size_hint_y=None, adaptive_height=True,
                                              num_of_exc=num_of_exc, num_of_set=num_of_set,
                                              screen="Third")

        set_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, None), padding='10dp', spacing='10dp',
                                 adaptive_height=True)

        num_lbl = MDLabel(text=(str(num_of_set) + "-"), size_hint=(None, None),
                          size=("40dp", "40dp"), pos_hint={"center_y": .5}, adaptive_height=True)

        time_input = MDTextField(pos_hint={"center_y": .5})

        if str(type_of_exc).replace("\n", "") == "Время":
            time_input.validator = "time"
            time_input.add_widget(MDTextFieldHelperText(text="Формат текста: 00:00"))
            time_input.add_widget(MDTextFieldHintText(text="Время подхода"))
        else:
            time_input.add_widget(MDTextFieldHintText(text="Количество повторений"))

        set_layout.add_widget(num_lbl)
        set_layout.add_widget(time_input)
        set_layout.ids["time_input"] = time_input
        set_layout.ids["exercise_num_lbl"] = num_lbl
        set_layout_holder.ids["front_box"].add_widget(set_layout)
        set_layout_holder.ids["front_box"].ids["exercise_set_layout"] = set_layout
        layout.add_widget(set_layout_holder)

    def menu_open(self, initiator, layout, exercise):
        menu_items = [
            {"text": "Изменить время отдыха",
             "on_release": lambda y=exercise: self.change_screen(y)
             },
            {"text": "Удалить упражнение",
             "on_release": lambda x=layout: self.delete_exc(x)
             }
        ]

        MDDropdownMenu(caller=initiator, items=menu_items, position="bottom"
                       ).open()

    def delete_exc(self, layout):
        print("deleting exercise..................")
        del self.nums_of_set[layout.ids["add_set_btn"].num_of_exc - 1]
        self.num_of_exercise -= 1
        self.parent_layout.remove_widget(layout)
        print("self.num_of_exercise: ", self.num_of_exercise)
        print("self.nums_of_set: ", self.nums_of_set)

    def delete_set(self, layout):
        print("Im deleting a set for third screen! (actually not doing anything rn)")

        child_var = self.parent_layout.children[:]  # child_var are all some_layouts
        child_var.reverse()
        holder = layout.parent  # The needed holder but faster
        some_layout = holder.parent  # The some_layout that is the parent of the holder
        some_layout.ids["add_set_btn"].num_of_set -= 1
        holder.remove_widget(layout)
        self.nums_of_set[layout.num_of_exc - 1] -= 1

        holder_children = holder.children[:]
        holder_children.reverse()
        for child in holder_children:  # child = exercise_set_layout_holder
            if child.num_of_set > layout.num_of_set:
                child.num_of_set -= 1
                child_var_2 = child.ids["front_box"].ids["exercise_set_layout"]
                child_var_2.ids["exercise_num_lbl"].text = str(child.num_of_set)

    def complete_template(self, initiator):
        all_additional_info = []
        all_primary_info = []
        num_of_exercise = 0
        template_name = self.name_input.text
        print(template_name)
        with open(path.join("templates", (str(template_name) + ".txt")), "w", encoding="utf-8") as file:
            children = self.parent_layout.children
            children.reverse()
            for child in children:  # child in this case being some_layout
                num_of_set = 0
                num_of_exercise += 1
                upper_layout = child.ids["upper_layout"]
                name_of_exc = upper_layout.ids["exc_name_lbl"].text
                holder = child.ids["holder"]
                children_var_1 = holder.children
                children_var_1.reverse()
                for child_var in children_var_1:  # child_var being the set_layout
                    try:
                        num_of_set += 1
                        print("num_of_set: ", num_of_set)
                        child_var_2 = child_var.ids["front_box"].ids["exercise_set_layout"]
                        type_of_exc = child_var_2.ids["time_input"].validator

                        # Может быть и повторения, а не время
                        time = child_var_2.ids["time_input"].text

                        if type_of_exc == "time" and time:
                            time = convert_text_to_seconds(time)
                        else:
                            print("type_of_exc: ", type_of_exc)
                        # additional_info = str(num_of_exercise) + str(num_of_set) + str(time) + ", "
                        all_additional_info.append(str(num_of_exercise))
                        all_additional_info.append(str(num_of_set))
                        all_additional_info.append(str(time))
                    except IndexError:
                        continue
                all_primary_info.append(str(num_of_set) + "\n")
                all_primary_info.append(name_of_exc + "\n")
            for info_item in all_primary_info:
                file.write(info_item)
            for info_item in all_additional_info:
                file.write(info_item + ", ")
        app.change_to_First(True)

    def change_screen(self, exercise):
        app.change_to_Fifth('Third', exercise, False)


class FourthScreen(MDScreen):
    previous_screen = None

    def __init__(self, **kwargs):
        super(FourthScreen, self).__init__(**kwargs)

    def make_info_popup(self, widget):
        filename = widget.text + ".txt"
        file = open(path.join('exercises', filename), 'r', encoding='utf-8')
        # Имя на санскрите, время отдыха, рабочие группы мышц (или функция упражнения, или его польза)
        # Тип упражнения (время или повторения), фото упражнения,
        # как делать упражнение, соответственно:
        s_name, rest_time, muscles, exc_type, image, *instructions = file.readlines()

        s_name = str(s_name)
        muscles = str(muscles)
        exc_type = str(exc_type)
        lbl_text = [str(s_name), str(exc_type), str(muscles)]
        for instruction in instructions:
            lbl_text.append(instruction)
        for x in lbl_text:
            x = x.replace("\n", "")
        file.close()

        # TODO: find a way to make the dialog bigger (in height)
        self.dialog = MDDialog(
            MDDialogIcon(icon='information'),
            MDDialogHeadlineText(text="Информация о упражнении"),
            CustomMDDialogContentContainer(info=lbl_text, image=image, size_hint=(1, 1)
                                           ),
            MDDialogButtonContainer(
                Widget(),
                MDButton(
                    MDButtonText(text="Отмена"),
                    on_press=self.on_cancel_button_press),
                spacing="8dp"),
            size_hint=(1, 1))
        self.dialog.open()

    def on_enter(self, *args):
        main_widget = PreviousExercises()
        self.add_widget(main_widget)
        main_widget.set_list_md_icons()

    def on_cancel_button_press(self, instance):
        self.dialog.dismiss()

    def set_previous_screen(self, screen):
        self.previous_screen = screen


class CustomMDDialogContentContainer(MDDialogContentContainer):
    def __init__(self, *args, info, image, **kwargs):
        super().__init__(*args, **kwargs)
        self.orientation = "vertical"
        layout_root = MDScrollView(do_scroll_x=False, do_scroll_y=True, size_hint_y=None, height=app.root.height*0.5)
        layout = MDBoxLayout(orientation="vertical", size_hint=(1, None), adaptive_height=True,
                             padding="10dp", spacing="10dp")
        layout.add_widget(MDDivider())

        if image and ("None" not in image):
            img = FitImage(source=path.join("images", image.replace("\n", "")), size_hint=(1, None),
                           keep_ratio=True, allow_stretch=True, height="300dp")
            layout.add_widget(img)
            layout.add_widget(MDDivider())
        for text_item in info:
            layout.add_widget(MDLabel(text=text_item, size_hint_y=None, adaptive_height=True))
        layout.add_widget(MDDivider())
        layout_root.add_widget(layout)
        self.add_widget(layout_root)
        # self.add_widget(layout)


class CustomOneLineIconListItem(MDListItem):
    icon = StringProperty()
    text = StringProperty()


# Yes I did steal it from icon_definitions.py. Deal with it.
class PreviousExercises(MDScreen):
    def set_list_md_icons(self, text="", search=False):
        """Builds a list of exercises for the FourthScreen."""

        def add_exercise_item(name_exercise):
            self.ids.rv.data.append(
                {
                    "viewclass": "CustomOneLineIconListItem",
                    "text": name_exercise,
                    "callback": lambda x: x,
                }
            )

        self.ids.rv.data = []
        for name_exercise in exercise_items:
            if search:
                if text in name_exercise:
                    add_exercise_item(name_exercise)
            else:
                add_exercise_item(name_exercise)


class FifthScreen(MDScreen):
    time_val_1 = 60
    time_val_2 = 120
    time_val_3 = 180
    time_val_4 = 240
    past_screen = None  # This is the screen from which the FifthScreen was called
    exercise_that_needs_to_change_time = None  # This is a long name
    current_past_screen = None
    text = None
    need_to_rest = False  # If true when pressing any of the time buttons the rest() function will start

    # created = False
    # need_to_clear = False

    def __init__(self, **kwargs):
        """
        Imitation is the greatest form of flattery. I said this because I stole the design.
        :param kwargs:
        """
        super(FifthScreen, self).__init__(**kwargs)

    def create_widgets(self):
        # if self.created:
        #    if self.past_screen != self.current_past_screen:
        #        self.need_to_clear = True
        # if self.need_to_clear:
        #    self.clear_widgets()
        #    print("clearing widgets..")
        self.time_values = [self.time_val_1, self.time_val_2, self.time_val_3, self.time_val_4]
        top_app_bar = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="arrow-left", on_press=partial(app.change_to_screen, self.past_screen)
                )),
            MDTopAppBarTitle(text="Таймер отдыха"),
            type="small", pos_hint={"center_x": .5, "top": 1}, size_hint=(1, None)
        )

        self.add_widget(top_app_bar)

        layout = MDBoxLayout(orientation="vertical", size_hint=(1, None), pos_hint={"center_y": .5},
                             padding="6dp", spacing="6dp", adaptive_height=True)
        self.progress_bar = CircularProgressBar(pos_hint={"center_x": .5, "center_y": .5}, size_hint=(None, None),
                                                size=("400dp", "400dp"))
        self.box = MDBoxLayout(orientation="vertical", size_hint=(1, None), spacing="5dp")
        self.progress_bar.add_widget(self.box)
        layout.add_widget(self.progress_bar)

        for time_val in self.time_values:
            text_var = convert_seconds_to_text(time_val)
            time_val_btn = MDButton(MDButtonText(text=text_var), pos_hint={"center_x": .5}, size_hint=(1, 1.5))
            time_val_btn.bind(on_press=partial(self.rest, time_val))
            self.box.add_widget(time_val_btn)

        self.add_widget(layout)
        # with layout.canvas:
        #    Color(.157, .174, .017, 1)
        #    Ellipse(size=(self.width, self.height))
        #    Color(0, .128, .129, 1)
        #    Ellipse(size=(self.width * .9, self.height * .9))
        add_own_timer_btn = MDButton(MDButtonText(text="Добавить свой таймер"), size_hint_x=2,
                                     pos_hint={"bottom": 1, "center_x": .5})
        add_own_timer_btn.bind(on_press=self.add_own_timer)
        self.add_widget(add_own_timer_btn)
        self.current_past_screen = self.past_screen
        # self.need_to_clear = False

    def rest(self, time, initiator):
        print(f"I start timer with {time} time. I was initialized by: {initiator}")
        if not self.need_to_rest:
            write_new_exercise_rest_time(time, self.exercise_that_needs_to_change_time)
            self.exercise_that_needs_to_change_time = None
            app.change_to_screen(self.past_screen)
        # self.progress_bar.duration = int(time)
        # Clock.schedule_once(self.progress_bar.animate, 0)
        else:
            if time not in self.time_values:
                self.time_values.insert(0, time)
                self.time_val_1, self.time_val_2, self.time_val_3, self.time_val_4, *args = self.time_values
            app.change_to_Sixth(time)

    def add_own_timer(self, initiator):
        app.change_to_Seventh()

    def set_past_screen(self, screen, exercise, mode, *args):
        self.need_to_rest = mode
        if exercise:
            self.exercise_that_needs_to_change_time = exercise
        print("setting_past_screen to: ", screen)
        self.past_screen = screen
        global past_fifthscreen_val
        past_fifthscreen_val = screen

    def return_time_value(self):
        pass


def change_sm_to_past_screen(*args):
    app.sm.current = past_fifthscreen_val


# [0.615686274509804, 0.6823529411764706, 0.06666666666666667]
class CircularProgressBar(AnchorLayout):
    bar_color = ListProperty([128 / 255, 128 / 255, 1 / 255])
    value = NumericProperty(100)
    bar_width = NumericProperty(10)
    set_value = NumericProperty(0)
    duration = NumericProperty(10)
    text = StringProperty("")
    counter = 0

    def __init__(self, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)
        # self.ids["box"] = box
        #self.image = img
        #if self.image:
        #    self.add_image()

    def animate(self, *args):
        Clock.schedule_interval(self.percent_counter, 1)

    def unschedule_percent_counter(self, *args):
        Clock.unschedule(self.percent_counter)

    def percent_counter(self, dt):
        if self.counter < self.duration:
            self.counter += 1
            self.parent.parent.time_label.text = convert_seconds_to_text(self.duration - self.counter)
            self.set_value += 100 / self.duration
        else:
            Clock.unschedule(self.percent_counter)
            sound_rest.play()
            self.return_to_normal()

    def return_to_normal(self):
        self.counter = 0
        self.set_value = 0
        change_sm_to_past_screen()

    #def add_image(self):
    #    with self.canvas:
    #        Ellipse(source=self.image, angle_start=0, angle_end=360)


class SixthScreen(MDScreen):
    text = StringProperty("")
    time_val = NumericProperty(5)
    # past_screen = past_fifthscreen_val
    need_to_update = True
    created = False

    def __init__(self, **kwargs):
        super(SixthScreen, self).__init__(**kwargs)
        self.create_widgets()

    def create_widgets(self):
        # I'm pretty sure that this is a bad way to dynamically update the screens.
        # if self.need_to_update:
        #    if self.created:
        #        app.sm.current_screen.clear_widgets()
        top_app_bar = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="arrow-left", on_press=self.stop
                )),
            MDTopAppBarTitle(text="Таймер отдыха"),
            type="small", pos_hint={"center_x": .5, "top": 1}, size_hint=(1, None)
        )

        self.add_widget(top_app_bar)
        layout = MDBoxLayout(orientation="vertical", size_hint=(1, None), pos_hint={"center_y": .5},
                             padding="6dp", spacing="6dp", adaptive_height=True)
        self.progress_bar = CircularProgressBar(pos_hint={"center_x": .5, "center_y": .5}, size_hint=(None, None),
                                                size=("400dp", "400dp"))
        self.time_label = MDLabel(text=self.text, pos_hint={"center_x": .5, "center_y": .5}, font_size=sp(40),
                                  halign="center")
        self.progress_bar.add_widget(self.time_label)
        layout.add_widget(self.progress_bar)

        bottom_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, spacing="50dp", padding="10dp",
                                    pos_hint={"bottom": 1})  # center_x: .5
        add_time_btn = MDButton(MDButtonText(text=f"+{str(self.time_val)}c."), pos_hint={"center_x": .25})
        add_time_btn.bind(on_press=self.add_time)

        extract_time_btn = MDButton(MDButtonText(text=f"-{str(self.time_val)}c."), pos_hint={"center_x": .75})
        extract_time_btn.bind(on_press=self.extract_time)

        bottom_layout.add_widget(add_time_btn)
        bottom_layout.add_widget(extract_time_btn)
        self.add_widget(layout)
        self.add_widget(bottom_layout)
        # self.need_to_update = False
        # self.created = True

    def add_time(self, *args):
        self.progress_bar.duration += self.time_val
        self.progress_bar.set_value = self.progress_bar.counter * (100 / self.progress_bar.duration)

        self.progress_bar.unschedule_percent_counter()
        self.progress_bar.animate()

    def extract_time(self, *args):
        self.progress_bar.duration -= self.time_val
        self.progress_bar.set_value = self.progress_bar.counter * (100 / self.progress_bar.duration)

        self.progress_bar.unschedule_percent_counter()
        self.progress_bar.animate()

    def start(self, time, *args):
        self.progress_bar.duration = time
        self.progress_bar.animate()

    def stop(self, *args):
        Clock.unschedule(self.progress_bar.percent_counter)
        self.progress_bar.return_to_normal()
        change_sm_to_past_screen()


class SeventhScreen(MDScreen):
    text_var = StringProperty("")

    def __init__(self, **kwargs):
        super(SeventhScreen, self).__init__(**kwargs)
        self.create_widgets()

    def create_widgets(self):
        # layout_root = MDBoxLayout(orientation="vertical", size_hint=(1, None), adaptive_height=True,
        #                         padding="15dp", spacing="15dp")
        # layout_root.bind(minimum_height=layout_root.setter('height'))

        self.exit_btn = MDActionTopAppBarButton(icon="arrow-left-bold", size_hint=(None, None), size=("30dp", "30dp"))
        self.exit_btn.bind(on_press=self.exit)
        upper_layout = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(self.exit_btn),
            MDTopAppBarTitle(text="Таймер отдыха", pos_hint={"center_x": .5}),
            type="small", pos_hint={"top": 1}
        )
        self.add_widget(upper_layout)
        # self.add_widget(layout_root)
        info_lbl = MDLabel(text="Пользовательская длительность будет сохранена в следующий раз",
                           adaptive_height=True, pos_hint={"y": .8})
        self.add_widget(info_lbl)

        # layout_root.add_widget(info_lbl)

        self.time_slider = CustomMDSlider(
            MDSliderHandle(
            ),
            MDSliderValueLabel(
            ),
            step=5, value=60, min=5, max=600, pos_hint={"center_x": .5, "center_y": .5}, size_hint_x=.95
        )

        # layout_root.add_widget(self.time_slider)
        self.add_widget(self.time_slider)
        add_time_btn = MDButton(MDButtonIcon(icon="plus"), MDButtonText(text="Добавить своё время"),
                                pos_hint={"center_x": .5, "bottom": 1})
        add_time_btn.bind(on_press=self.add_time)
        self.add_widget(add_time_btn)
        # layout_root.add_widget(add_time_btn)

    def exit(self, *args):
        app.sm.current = "Fifth"

    def add_time(self, initiator):
        app.get_running_app().root.get_screen("Fifth").rest(self.time_slider.value, initiator)


class AutoMode(MDScreen):
    def create_widgets(self):
        # ScrollView?
        layout_root = MDBoxLayout(orientation='vertical', padding="15dp", spacing="15dp")  # adaptive_height?
        upper_layout = MDBoxLayout(orientation='horizontal', padding="3dp", spacing="2dp", size_hint=(1, None),
                                   adaptive_height=True)
        exit_btn = MDButton(MDButtonText(text="Выход"))
        exit_btn.bind(on_release=self.exit_auto_mode)
        upper_layout.add_widget(exit_btn)
        layout_root.add_widget(upper_layout)
        timer_layout = MDBoxLayout(orientation="vertical", spacing="15dp", padding="5dp", size_hint=(1, 1))
                                   #adaptive_height=True)
        circle_timer = CircularProgressBar(pos_hint={"center_x": .5, "center_y": .5}, size_hint=(None, None),
                                           size=("400dp", "400dp"), img="bear.png")
        timer_layout.add_widget(circle_timer)
        timer_lbl = MDLabel(text="test_timer_lbl_text", size_hint=(.5, .5),
                            pos_hint={"center_x": .5, "center_y": .5})
        timer_layout.add_widget(timer_lbl)
        layout_root.add_widget(timer_layout)
        lower_layout = MDBoxLayout(orientation="horizontal", padding="5dp", spacing="5dp", adaptive_height=True)
        # TODO: maybe make this button bigger?
        next_activity_btn = MDButton(MDButtonText(text="Следующее:\n PLACEHOLDER_TEXT", halign="center"),
                                     pos_hint={"center_x": 1, "center_y": .5})
        next_activity_btn.bind(on_release=self.go_to_next_activity)
        lower_layout.add_widget(next_activity_btn)
        layout_root.add_widget(lower_layout)
        self.add_widget(layout_root)


    def exit_auto_mode(self, *args):
        print("I exit auto mode")

    def go_to_next_activity(self, *args):
        print("I go to next activity")


if __name__ == '__main__':
    app = YogaApp()
    app.run()
