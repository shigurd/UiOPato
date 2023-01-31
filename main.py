# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
import json
import random
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

class SlideEntry:
    def __init__(self, slide_dict):
        self.slide_set = slide_dict['slide_set']
        self.slide_link = slide_dict['slide_link']
        self.slide_text = slide_dict['slide_text']
        self.slide_comment = slide_dict['slide_comment']
        self.slide_goal = slide_dict['slide_goal']
        self.extra_slide_id = slide_dict['extra_slide_id']
        self.m8_status = slide_dict['m8_status']


def check_tag_in_string(slide, comma_sepatered_tags_list):
    question_string = slide.slide_set
    question_string += ' ' + slide.slide_text
    question_string += ' ' + slide.slide_comment
    question_string += ' ' + slide.slide_goal

    #input_string_lower = question_string.lower()
    #tag_list_lower = [tag.lower() for tag in comma_sepatered_tags_list]

    include = False
    for t in comma_sepatered_tags_list:
        if t in question_string:
            include = True

    return include

def input_tags_to_list(input_tags_string):
    comma_sepatered_tags_list = input_tags_string.split(',')
    comma_sepatered_tags_list = [i.strip(' ') for i in comma_sepatered_tags_list]

    return comma_sepatered_tags_list


class QuizApp(tk.Tk):
    def __init__(self, file_path_list):
        tk.Tk.__init__(self)
        self.file_path_list = file_path_list
        self.configs_tk = {'font': 'Helvetica 12',
                           'font_i': 'Helvetica 12 italic',
                           'font_b': 'Helvetica 12 bold',
                           'w_length': 800,
                           'color_orange': '#fed06a',
                           'color_green': '#88d8b0',
                           'color_grey': '#626262',
                           'color_red': '#f96e5a',
                           'color_blue': '#65cbda'}
        self.order_var = tk.StringVar()
        self.m8_var = tk.StringVar()
        self.category_list = ['Modul 3', 'Modul 6', 'Modul 8']
        self.order_mode = ['Kronologisk', 'Tilfeldig']
        self.m8_mode = ['Ja', 'Nei']
        self.filter_tags = []
        self.title('UiO Patologi')
        self.geometry('960x1000')
        self.frame_main = tk.Frame(self)
        self.frame_main.pack(fill=tk.BOTH, expand=1)
        self.create_scrollbar()

        self.create_frame_menu()
        self.count_relative = tk.IntVar()
        self.choice_var = tk.StringVar()


    #def _on_mousewheel(self, event):
    #    print(event.delta)
    #    self.canvas_main.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_scrollbar(self):
        self.canvas_main = tk.Canvas(self.frame_main)
        self.canvas_main.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = tk.Scrollbar(self.frame_main, orient=tk.VERTICAL, command=self.canvas_main.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas_main.configure(yscrollcommand=scrollbar.set)
        self.canvas_main.bind('<Configure>', lambda e:self.canvas_main.configure(scrollregion=self.canvas_main.bbox("all")))
        #self.canvas_main.bind_all("<MouseWheel>", self._on_mousewheel)


    def create_slide_dock_container(self):
        self.dock_container = tk.Frame(self.frame_slide)
        self.dock_container.grid(row=0, column=0, sticky='')

        # Create progress bar
        self.progress_container = tk.Frame(self.dock_container)
        self.progress_container.pack()

        self.count_relative.set(int(self.current_slide_index + 1) * 100 / len(self.slides))
        self.progress_count = tk.StringVar()
        self.progress_count.set(f'Progresjon: {self.current_slide_index + 1} / {len(self.slides)} ({int((self.current_slide_index + 1) * 100 / len(self.slides))}%)')
        progress_number = tk.Label(self.progress_container, textvariable=self.progress_count, font=self.configs_tk['font_i'])
        progress_number.grid(row=0, column=1)

        progress_bar = ttk.Progressbar(self.progress_container, variable=self.count_relative, orient='horizontal', length=500,
                                            mode='determinate')
        progress_bar.grid(row=1, column=1)


        # Create button bar
        self.button_container = tk.Frame(self.dock_container)
        self.button_container.pack()

        menu_button = tk.Button(self.button_container, text='MENY', command=self.on_menu, bg=self.configs_tk['color_grey'], fg='white', height=1, width=13, font=self.configs_tk['font'])
        self.show_button = tk.Button(self.button_container, text='FASIT', command=self.on_show, bg='white', fg='black', height=1, width=13, font=self.configs_tk['font'])
        previous_button = tk.Button(self.button_container, text='SKIP', command=self.on_skip, bg=self.configs_tk['color_orange'], height=1, width=13, font=self.configs_tk['font'])
        menu_button.grid(row=0, column=0)
        self.show_button.grid(row=0, column=1)
        previous_button.grid(row=0, column=2)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service('chromedriver.exe')
        self.driver = webdriver.Chrome(options=options, service=service)


    def create_extra_button_container(self):
        self.extra_button_container = tk.Frame(self.frame_slide)
        self.extra_button_container.grid(row=1, column=0, sticky='')

        if len(self.slides[self.current_slide_index].extra_slide_id) != 0:

            org_button = tk.Button(self.extra_button_container, text=f'H&E', command=lambda:self.on_link_button(self.slides[self.current_slide_index].slide_link), font=self.configs_tk['font'],
                                   height=1, width=13, bg='white')
            org_button.grid(row=0, column=0)

            self.extra_link_vars = []

            for r in self.slides[self.current_slide_index].extra_slide_id:
                self.extra_link_vars.append(tk.StringVar())
                self.extra_link_vars[-1] = r[0]
                button = tk.Button(self.extra_button_container, text=f'{r[1]}', command=lambda x=r[0]:self.on_link_button(x), bg='white', font=self.configs_tk['font'], height=1, width=13)
                button.grid(row=0, column=len(self.extra_link_vars))


    def create_slide_container(self):
        self.slide_container = tk.Frame(self.frame_slide)
        self.slide_container.grid(row=2, column=0, sticky='w')

        self.driver.get(self.slides[self.current_slide_index].slide_link)

        self.slide_answer = tk.Label(self.slide_container, text='', font=self.configs_tk['font_b'], pady=10)
        self.slide_answer.pack()

        history_id = tk.Label(self.slide_container, text='Sykehistorie:', font=self.configs_tk['font_i'], justify='left', wraplength=self.configs_tk['w_length'], pady=10)
        history_id.pack(anchor='w')

        history_text_id = tk.Label(self.slide_container, text=self.slides[self.current_slide_index].slide_text, font=self.configs_tk['font'], justify='left',
                                   wraplength=self.configs_tk['w_length'])
        history_text_id.pack(anchor='w')

        self.comment_id = tk.Label(self.slide_container, text='', font=self.configs_tk['font_i'], justify='left',
                                   wraplength=self.configs_tk['w_length'], pady=10)
        self.comment_id.pack(anchor='w')

        self.comment_text_id = tk.Label(self.slide_container, text='',
                                        font=self.configs_tk['font'], justify='left',
                                        wraplength=self.configs_tk['w_length'])
        self.comment_text_id.pack(anchor='w')

        self.goal_id = tk.Label(self.slide_container, text='', font=self.configs_tk['font_i'], justify='left',
                                wraplength=self.configs_tk['w_length'], pady=10)
        self.goal_id.pack(anchor='w')

        self.goal_text_id = tk.Label(self.slide_container, text='',
                                     font=self.configs_tk['font'], justify='left',
                                     wraplength=self.configs_tk['w_length'])
        self.goal_text_id.pack(anchor='w')


    def create_frame_slide(self):
        self.frame_slide = tk.Frame(self.canvas_main, pady=20, padx=80)
        self.canvas_main.create_window((0, 0), window=self.frame_slide, anchor="nw")
        self.frame_slide.bind('<Configure>', lambda e: self.canvas_main.configure(scrollregion=self.canvas_main.bbox("all")))

        self.create_slide_dock_container()
        self.create_extra_button_container()
        self.create_slide_container()


    def create_module_box_container(self):
        self.category_box_container = tk.Frame(self.lower_menu_container)
        self.category_box_container.grid(row=1, column=0, sticky='nw')

        box_label = tk.LabelFrame(self.category_box_container, text='MODUL', font=self.configs_tk['font_b'], padx=40, pady=20)
        box_label.pack()
        self.check_label_category = []
        self.check_label_category_vars = []

        for e in self.category_list:
            self.check_label_category_vars.append(tk.IntVar())
            check_label = tk.Checkbutton(box_label, text=e, variable=self.check_label_category_vars[-1], font=self.configs_tk['font'])
            self.check_label_category.append(check_label)
            check_label.pack(anchor='w')

        select_all_button = tk.Button(box_label, text='Velg alle', command=lambda:self.on_selectall(self.check_label_category),
                                      bg='white', font=self.configs_tk['font'],
                                      height=1, width=7)
        remove_all_button = tk.Button(box_label, text='Fjern alle', command=lambda:self.on_deselectall(self.check_label_category),
                                      bg='white', font=self.configs_tk['font'],
                                      height=1, width=7)
        select_all_button.pack()
        remove_all_button.pack()


    def create_order_box_container(self):
        self.order_box_container = tk.Frame(self.lower_menu_container)
        self.order_box_container.grid(row=1, column=1, sticky='nw')

        box_label = tk.LabelFrame(self.order_box_container, text='REKKEFØLGE', font=self.configs_tk['font_b'], padx=40, pady=20)
        box_label.pack()

        self.order_var.set('0')
        for r in self.order_mode:
            button = tk.Radiobutton(box_label, text=r, variable=self.order_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')


    def create_m8_box_container(self):
        self.order_box_container = tk.Frame(self.lower_menu_container)
        self.order_box_container.grid(row=1, column=2, sticky='nw')

        box_label = tk.LabelFrame(self.order_box_container, text='M8 MODUS', font=self.configs_tk['font_b'], padx=40, pady=20)
        box_label.pack()

        self.m8_var.set('0')
        for r in self.m8_mode:
            button = tk.Radiobutton(box_label, text=r, variable=self.m8_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')


    def create_menu_dock_container(self):
        self.start_container = tk.Frame(self.upper_menu_container)
        self.start_container.pack()

        start_button = tk.Button(self.start_container, text='START', command=self.on_start, bg=self.configs_tk['color_green'], height=1,
                                       width=13, font=self.configs_tk['font'])
        start_button.grid(row=1, column=2)

        stats_button = tk.Button(self.start_container, text='VIS UTVALG', command=self.on_check,
                                 bg='white', height=1, width=13, font=self.configs_tk['font'])
        stats_button.grid(row=1, column=3)

        self.remaining_questions_number = tk.Label(self.start_container, text='Utvalg slides: 0',
                                                   font=self.configs_tk['font_i'], justify='left',
                                                   wraplength=self.configs_tk['w_length'])
        self.remaining_questions_number.grid(row=0, column=4, sticky='nw')
        white_space = tk.Label(self.start_container, text='UiO Medisin',
                                                   font=self.configs_tk['font_i'], justify='left',
                                                   wraplength=self.configs_tk['w_length'])
        white_space.grid(row=0, column=0, sticky='nw')


    def create_menu_info_container(self):
        self.menu_info_container = tk.Frame(self.frame_menu)
        self.menu_info_container.pack(anchor='w')

        instructions_text = tk.Label(self.menu_info_container,
                             text='INSTRUKSER:', font=self.configs_tk['font_b'], justify='left',
                             wraplength=self.configs_tk['w_length'])
        instructions_text.pack(anchor='w')
        info_text = tk.Label(self.menu_info_container, text='START: Starter quiz for utvalget. Fullførte oppgaver ekskluderes med mindre de tilbakestilles.\nVIS UTVALG: Viser antall oppgaver og fullføringsgrad for utvalget.', font=self.configs_tk['font_i'], justify='left',
                               wraplength=self.configs_tk['w_length'])
        info_text.pack(anchor='w')


    def create_tag_filter_container(self):
        self.tag_filter_container = tk.Frame(self.frame_menu)
        self.tag_filter_container.pack(anchor='w', pady=20)

        info_text = tk.Label(self.tag_filter_container,
                             text='STIKKORD FILTER:', font=self.configs_tk['font_b'], justify='left',
                             wraplength=self.configs_tk['w_length'])
        info_text.pack(anchor='w')
        filter_explaination = tk.Label(self.tag_filter_container, text='Filtrerer oppgaver i utvalget basert på ønskede stikkord. Bruk "," mellom hvert stikkord (case sensitivt). Tomt filter inkluderer alle oppgaver for utvalget.', font=self.configs_tk['font_i'], justify='left',
                             wraplength=self.configs_tk['w_length'])
        filter_explaination.pack(anchor='w')

        self.tag_input = tk.Text(self.tag_filter_container, font=self.configs_tk['font'], height=1, borderwidth=0)
        self.tag_input.pack(anchor='w')

    def create_source_info_container(self):
        self.source_info_container = tk.Frame(self.frame_menu)
        self.source_info_container.pack(anchor='w')
        sources_text = tk.Label(self.source_info_container,
                                text='KILDER:', font=self.configs_tk['font_b'], justify='left',
                                wraplength=self.configs_tk['w_length'])
        sources_text.pack(anchor='w')
        sources_link = tk.Text(self.source_info_container, font=self.configs_tk['font'], height=2, borderwidth=0)
        sources_link.insert(1.0,
                    'https://studmed.uio.no/elaring/fag/patologi/index.shtml\nhttps://github.com/shigurd/UiOPato')
        sources_link.configure(state='disabled')
        sources_link.pack(anchor='w')

    def create_shoutout_container(self):
        self.shoutout_container = tk.Frame(self.frame_menu)
        self.shoutout_container.pack(anchor='w', pady=20)
        shoutout_text = tk.Label(self.shoutout_container,
                                text='Doner til MedHum ( ´◉◞౪◟◉)୨', font=self.configs_tk['font_i'], justify='left',
                                wraplength=self.configs_tk['w_length'])
        shoutout_text.pack(anchor='w')
        shoutout_link = tk.Text(self.shoutout_container, font=self.configs_tk['font'], height=1, borderwidth=0)
        shoutout_link.insert(1.0,'https://www.medhum.no/')
        shoutout_link.configure(state='disabled')
        shoutout_link.pack(anchor='w')

    def create_frame_menu(self):
        self.slides = []
        self.current_slide_index = 0
        self.filter_tags = []

        self.frame_menu = tk.Frame(self.canvas_main, pady=20, padx=80)
        self.canvas_main.create_window((0, 0), window=self.frame_menu, anchor="nw")
        self.frame_menu.bind('<Configure>',lambda e: self.canvas_main.configure(scrollregion=self.canvas_main.bbox("all")))

        self.upper_menu_container = tk.Frame(self.frame_menu)
        self.upper_menu_container.pack()
        self.create_menu_dock_container()

        self.create_menu_info_container()
        self.create_tag_filter_container()

        self.lower_menu_container = tk.Frame(self.frame_menu)
        self.lower_menu_container.pack()
        self.create_module_box_container()
        self.create_order_box_container()
        self.create_m8_box_container()

        self.create_source_info_container()
        self.create_shoutout_container()

    def create_quiz_page(self):
        self.frame_menu.destroy()
        self.create_frame_slide()

    def on_link_button(self, link):
        self.driver.get(link)

    def on_check(self):
        included_category_tags = []
        for c in zip(self.category_list, self.check_label_category_vars):
            if c[1].get() == 1:
                included_category_tags.append(c[0])

        included_paths = []
        for pth in self.file_path_list:
            no_ext = pth.rsplit('.', 1)[0].lower()
            for ct in included_category_tags:
                if ct.lower() in no_ext:
                    included_paths.append(pth)

        included_slides = 0
        self.filter_tags = input_tags_to_list(self.tag_input.get("1.0", 'end-1c'))

        for pth in included_paths:
            file_json = open(pth, encoding="utf8")
            try:
                file_dict = json.load(file_json)
            except Exception as e:
                print(e)

            for q in range(1, len(file_dict) + 1):
                slide = SlideEntry(file_dict[f'{pth.rsplit(".", 1)[0].rsplit("_", 1)[-1]}_{q}'])

                if check_tag_in_string(slide, self.filter_tags):
                    if self.m8_var.get() == 'Ja':
                        if slide.m8_status == "1":
                            included_slides += 1
                    else:
                        included_slides += 1

        if included_slides > 0:
            self.remaining_questions_number.configure(text=f'Valge slides: {included_slides}')
        else:
            self.remaining_questions_number.configure(text=f'Valge slides: 0')


    def on_start(self):
        if self.order_var.get() != '0' and self.m8_var.get() != '0' and sum([cv.get() for cv in self.check_label_category_vars]) > 0:

            included_category_tags = []
            for c in zip(self.category_list, self.check_label_category_vars):
                if c[1].get() == 1:
                    included_category_tags.append(c[0])

            included_paths = []
            for pth in self.file_path_list:
                no_ext = pth.rsplit('.', 1)[0].lower()

                for ct in included_category_tags:
                    if ct.lower() in no_ext:
                        included_paths.append(pth)

            included_slides = []
            self.filter_tags = input_tags_to_list(self.tag_input.get("1.0", 'end-1c'))

            for pth in included_paths:
                file_json = open(pth, encoding="utf8")
                try:
                    file_dict = json.load(file_json)
                except Exception as e:
                    print(e)

                for q in range(1, len(file_dict) + 1):
                    slide = SlideEntry(file_dict[f'{pth.rsplit(".", 1)[0].rsplit("_", 1)[-1]}_{q}'])
                    if check_tag_in_string(slide, self.filter_tags):
                        if self.m8_var.get() == 'Ja':
                            if slide.m8_status == "1":
                                included_slides.append(slide)
                        else:
                            included_slides.append(slide)

            if self.order_var.get() == 'Tilfeldig':
                random.shuffle(included_slides)

            self.slides = included_slides

            if len(included_slides) > 0:
                self.create_quiz_page()


    def on_selectall(self, check_box_list):
        for i in check_box_list:
            i.select()

    def on_deselectall(self, check_box_list):
        for i in check_box_list:
            i.deselect()


    def on_skip(self):
        self.current_slide_index += 1
        if self.current_slide_index >= len(self.slides):
            self.frame_slide.destroy()
            self.driver.close()
            self.create_frame_menu()
        else:
            # Update the widgets with the new question
            self.count_relative.set(int(self.current_slide_index + 1) * 100 / len(self.slides))
            self.progress_count.set(f'Progresjon: {self.current_slide_index + 1} / {len(self.slides)} ({int((self.current_slide_index + 1) * 100 / len(self.slides))}%)')

            self.show_button.configure(text='FASIT', command=self.on_show, bg='white', fg='black')
            self.slide_container.destroy()
            self.extra_button_container.destroy()
            self.create_slide_container()
            self.create_extra_button_container()


    def on_menu(self):
        self.frame_slide.destroy()
        self.driver.close()
        self.create_frame_menu()


    def on_show(self):
        self.slide_answer.configure(text=f'{self.slides[self.current_slide_index].slide_set}')
        self.show_button.configure(text='NESTE', command=self.on_skip, bg=self.configs_tk['color_green'])

        self.comment_id.configure(text='Kommentar:')
        self.comment_text_id.configure(text=self.slides[self.current_slide_index].slide_comment)
        self.goal_id.configure(text='Læringsmål:')
        self.goal_text_id.configure(text=self.slides[self.current_slide_index].slide_goal)


if __name__ == '__main__':
    #pyinstaller main.spec
    os.chdir(os.path.join(os.path.dirname(sys.argv[0]), "lib"))


    question_set_json_pths = ['Modul 3_m3.json', 'Modul 6_m6.json', 'Modul 8_m8.json']
    app = QuizApp(question_set_json_pths)
    app.tkraise()
    app.mainloop()


