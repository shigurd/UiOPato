# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter import ttk
import json
import random
import os
import sys
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from webdriver_manager.chrome import ChromeDriverManager
from subprocess import CREATE_NO_WINDOW
import _thread
import time

class Gifplay:
    """
    Usage: mygif=gifplay(<<tkinter.label Objec>>,<<GIF path>>,<<frame_rate(in ms)>>)
    example:
    gif=GIF.gifplay(self.model2,'./res/neural.gif',0.1)
    gif.play()
    This will play gif infinitely
    """
    def __init__(self, label, giffile, delay):
        self.frame = []
        i = 0
        while 1:
            try:
                image = tk.PhotoImage(file=giffile, format="gif -index "+str(i))
                self.frame.append(image)
                i += 1
            except:
                break
        #print(i)
        self.totalFrames = i - 1
        self.delay = delay
        self.labelspace = label
        self.labelspace.image = self.frame[0]

    def play(self):
        """
        plays the gif
        """
        _thread.start_new_thread(self.infinite, ())

    def infinite(self):
        try:
            i = 0
            while 1:
                self.labelspace.configure(image=self.frame[i])
                i = (i + 1) % self.totalFrames
                time.sleep(self.delay)
        except:
            pass

class SlideEntry:
    def __init__(self, slide_dict):
        self.slide_set = slide_dict['slide_set']
        self.slide_link = slide_dict['slide_link']
        self.slide_text = slide_dict['slide_text']
        self.slide_comment = slide_dict['slide_comment']
        self.slide_goal = slide_dict['slide_goal']
        self.extra_slide_id = slide_dict['extra_slide_id']
        self.m8_status = slide_dict['m8_status']
        self.slide_notes = slide_dict['notes']
        self.json_name = slide_dict['json_name']
        self.slide_n = slide_dict['slide_n']

    def modify_json(self):
        file_pth = self.json_name

        with open(file_pth, "r",encoding="utf8") as file_json:
            file_dict_temp = json.load(file_json)

        file_dict_temp[f'{self.json_name.rsplit(".", 1)[0].rsplit("_", 1)[-1]}_{self.slide_n}']['notes'] = self.slide_notes

        with open(file_pth, "w", encoding="utf8") as file_json:
            json.dump(file_dict_temp, file_json)

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
    #comma_sepatered_tags_list = [i.strip(' ') for i in comma_sepatered_tags_list]

    return comma_sepatered_tags_list


class QuizApp(tk.Tk):
    def __init__(self, file_path_list):
        tk.Tk.__init__(self)
        self.file_path_list = file_path_list
        self.name = 'UiO PatoQuiz'
        self.version = '25.04.24'
        self.intro_gif = 'ascii-dog.gif'
        self.configs_tk = {'font': 'Helvetica 12',
                           'font_i': 'Helvetica 12 italic',
                           'font_b': 'Helvetica 12 bold',
                           'font_ib': 'Helvetica 12 italic bold',
                           'font_subtitle': 'Helvetica 20 bold italic',
                           'w_length': 765,
                           'w_length_menu': 700,
                           'color_white': '#ffffff',
                           'color_orange': '#fed06a',
                           'color_green': '#88d8b0',
                           'color_grey': '#626262',
                           'color_red': '#f96e5a',
                           'color_blue': '#65cbda'}
        self.quiz_order_mode_var = tk.StringVar()
        self.quiz_deactivate_mode_var = tk.StringVar()
        self.count_relative = tk.IntVar()
        self.quiz_module_list = ['Modul 3', 'Modul 6', 'Modul 8']
        self.quiz_order_mode_list = ['Kronologisk', 'Tilfeldig']
        self.quiz_deactivate_mode_list = ['Ja', 'Nei']
        self.quiz_filter_tags = []

        self.title(f'{self.name} {self.version}')
        self.state('zoomed')
        self.update_idletasks()  # update resolution
        self.max_width = self.winfo_width()
        self.max_height = self.winfo_height()
        self.create_root()
        self.create_scrollbar()

        self.create_intro_frame()
        self.current_mode = ''

    def _on_mousewheel(self, event):
        #print(event.delta)
        # code for free scroll
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_root(self):
        self.root_frame = tk.Frame(self)
        self.root_frame.pack(fill=tk.BOTH, expand=True)

    def create_scrollbar(self):
        self.main_canvas = tk.Canvas(self.root_frame)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.root_frame, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.main_canvas.bind('<Configure>', lambda e:self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel) #code for free scroll

    def create_intro_logo_label(self):
        self.intro_logo_container = tk.Frame(self.intro_frame)
        self.intro_logo_container.pack()

        logo_text = tk.Label(self.intro_logo_container, text=self.name, justify='left', font='Helvetica 50 bold italic',
                             pady=5)
        logo_text.pack()
        version_text = tk.Label(self.intro_logo_container, text=f'Versjon {self.version}', justify='left',
                                font=self.configs_tk['font_i'])
        version_text.pack()

        gif_label = tk.Label(self.intro_logo_container)
        gif_label.pack(padx=140, pady=5)
        mygif = Gifplay(gif_label, self.intro_gif, 0.2)
        mygif.play()

    def create_intro_buttons_container(self):
        self.intro_buttons_container = tk.Frame(self.intro_frame)
        self.intro_buttons_container.pack(pady=5)

        dummy_label = tk.Label(self.intro_buttons_container, text='', font=self.configs_tk['font_i'], height=2, width=4)
        dummy_label.grid(row=0, column=0, pady=5, padx=5)

        quiz_button = tk.Button(self.intro_buttons_container, text="PATOQUIZ", font=self.configs_tk['font_b'],
                                  bg=self.configs_tk['color_green'], height=2, width=30,
                                  command=lambda: self.create_quiz_menu_from_intro())
        quiz_button.grid(row=0, column=1, pady=5, padx=5)

        deactivate_button = tk.Button(self.intro_buttons_container, text="EGENDEFINER FILTER", font=self.configs_tk['font_b'],
                                      bg=self.configs_tk['color_orange'], height=2, width=30,
                                      command=lambda: self.create_deactivate_menu_from_intro())
        deactivate_button.grid(row=1, column=1, pady=5, padx=5)
        deactivate_info_button = tk.Menubutton(self.intro_buttons_container, text="Info", font=self.configs_tk['font_i'],
                                         bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'],
                                         relief='raised', height=2,
                                         width=4)
        deactivate_info_button.grid(row=1, column=2, pady=5, padx=5)
        deactivate_info_button.menu = tk.Menu(deactivate_info_button, tearoff=0)
        deactivate_info_button["menu"] = deactivate_info_button.menu
        deactivate_info_button.menu.add_cascade(
            label="Mulighet for mer detaljert seleksjon av spesifikke snitt fra alle moduler")
        deactivate_info_button.menu.add_cascade(
            label="Særlig relevant for Modul 8 eller om man ønsker å øve på spesifikke snitt")
        deactivate_info_button.menu.add_cascade(
            label="Det ligger predefinert et filter basert på eksamensforelesning Modul 8 Høst 2023")

        sources_button = tk.Button(self.intro_buttons_container, text="INFO OG KILDER", font=self.configs_tk['font_b'],
                                   bg=self.configs_tk['color_white'], height=2, width=30,
                                   command=lambda: self.create_sources_from_intro())
        sources_button.grid(row=4, column=1, pady=5, padx=5)

    def create_intro_shoutout_container(self):
        self.intro_shoutout_container = tk.Frame(self.intro_frame)
        self.intro_shoutout_container.pack(pady=10)

        shoutout_text = tk.Label(self.intro_shoutout_container,
                                 text='Doner til MedHum ( ´◉◞౪◟◉)୨', font='Helvetica 15 bold italic',
                                 wraplength=self.configs_tk['w_length'])
        shoutout_text.pack(pady=5)
        shoutout_link = tk.Text(self.intro_shoutout_container, font=self.configs_tk['font'], height=1, width=33,
                                borderwidth=0, )
        shoutout_link.insert(1.0, 'https://www.medhum.no/take-action')
        shoutout_link.configure(state='disabled')
        shoutout_link.pack(pady=5)

    def create_intro_frame(self):
        self.intro_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.intro_frame, anchor="n")
        self.intro_frame.bind('<Configure>',
                              lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_intro_logo_label()
        self.create_intro_buttons_container()
        self.create_intro_shoutout_container()

    def create_intro_from_any(self, current_frame):
        current_frame.destroy()
        if self.current_mode == 'EGENDEFINERT FILTER':
            #self.on_save_deactivate()
            pass
        elif self.current_mode == 'PATOQUIZ':
            self.driver.quit()
            try:
                self.save_notes()
                self.notes.destroy()
            except:
                pass
        self.current_mode = ''
        self.create_intro_frame()

    def create_subtitle_info_container(self, frame, title):
        menu_info_container = tk.Frame(frame, height=40, width=790)
        menu_info_container.pack(pady=10)

        subtitle_text = tk.Label(menu_info_container,
                                 text=title, font=self.configs_tk['font_subtitle'], justify='left',
                                 wraplength=self.configs_tk['w_length'])
        subtitle_text.pack(side=tk.LEFT)
        home_button = tk.Button(menu_info_container, text='Hjem',
                                command=lambda: self.create_intro_from_any(frame),
                                bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                height=1, width=10)
        home_button.pack(side=tk.RIGHT)
        menu_info_container.pack_propagate(False)

    def create_quiz_filter_container(self):
        quiz_tag_filter_container = tk.Frame(self.quiz_menu_frame)
        quiz_tag_filter_container.pack(pady=10)

        box_label = tk.LabelFrame(quiz_tag_filter_container,
                                  text='STIKKORDFILTER', font=self.configs_tk['font_b'], padx=32, pady=20)
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Skriv inn ønskede stikkord for å filtrere snittene i det underliggende snittutvalget')
        box_label_info_button.menu.add_cascade(
            label='Angitte stikkord søkes for i all tekst på snittsiden. Tomt filter inkluderer alle snitt for det underliggende snittutvalget')
        box_label_info_button.menu.add_cascade(
            label='Dersom flere stikkord er ønskelig, brukes "," for å skille stikkordene (dvs komma uten hermetegnene)')
        box_label_info_button.menu.add_cascade(
            label='Filteret skiller mellom store/små bokstaver, samt bruk av mellomrom. Det vil være forskjell på "slag" vs "slag " og "CT" vs "ct"')
        box_label_info_button.menu.add_cascade(
            label='Stikkordet "slag" vil inkludere snitt med ordene "hjerneslag", "slag" og "slagsmål". Derimot vil "slag " ekskludere "slagsmål" pga mellomrommet')
        box_label_info_button.menu.add_cascade(
            label='Et filter for slag-oppgaver kan feks være: Slag,slag ,Trombektomi,trombektomi,Trombolyse,trombolyse')

        self.quiz_text_input = tk.Text(box_label, font=self.configs_tk['font'], height=1)
        self.quiz_text_input.pack()

    def create_quiz_module_box_container(self):
        quiz_module_box_container = tk.Frame(self.quiz_menu_checkbox_container)
        quiz_module_box_container.grid(row=1, column=0, sticky='n')

        box_label = tk.LabelFrame(quiz_module_box_container, text='MODULER', font=self.configs_tk['font_b'], padx=30, pady=20, height=255, width=264)
        box_label.pack()
        self.quiz_check_label_module = []
        self.quiz_check_label_module_vars = []

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Valg av moduler for snittutvalget')

        for y in self.quiz_module_list:
            self.quiz_check_label_module_vars.append(tk.IntVar())
            check_label = tk.Checkbutton(box_label, text=y, variable=self.quiz_check_label_module_vars[-1],
                                         font=self.configs_tk['font'])
            self.quiz_check_label_module.append(check_label)
            check_label.pack(anchor='w')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

        select_all_button = tk.Button(box_label, text='Velg alle', command=lambda:self.on_selectall_quiz(self.quiz_check_label_module),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        select_all_button.pack(anchor='w')
        remove_all_button = tk.Button(box_label, text='Fjern alle', command=lambda:self.on_deselectall_quiz(self.quiz_check_label_module),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        remove_all_button.pack(anchor='w')

    def create_quiz_order_box_container(self):
        quiz_order_box_container = tk.Frame(self.quiz_menu_checkbox_container)
        quiz_order_box_container.grid(row=1, column=1, sticky='n')

        box_label = tk.LabelFrame(quiz_order_box_container, text='REKKEFØLGE', font=self.configs_tk['font_b'], padx=30, pady=20, height=255, width=264)
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                                bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                                width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Valg av rekkefølge for snittutvalget')
        box_label_info_button.menu.add_cascade(label='Kronologisk - Snittene kommer i rekkefølgen til UiOs patologiside')
        box_label_info_button.menu.add_cascade(label='Tilfeldig - Snittene i de ulike modulene blandes og kommer i tilfeldig rekkefølge')

        self.quiz_order_mode_var.set('0')
        for r in self.quiz_order_mode_list:
            button = tk.Radiobutton(box_label, text=r, variable=self.quiz_order_mode_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')
        box_label.pack_propagate(False) # makes height and width in labelframe active

    def create_quiz_deactivate_mode_container(self):
        deactivate_mode_container = tk.Frame(self.quiz_menu_checkbox_container)
        deactivate_mode_container.grid(row=1, column=2, sticky='n')

        box_label = tk.LabelFrame(deactivate_mode_container, text='EGENDEFINERT FILTER', font=self.configs_tk['font_b'], padx=30, pady=20, height=255, width=264)
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(
            label='Valg for aktivering av egendefinert filter for snittutvalget')
        box_label_info_button.menu.add_cascade(
            label='Det egendefinerte filteret har prioritet over stikkordfilteret')
        box_label_info_button.menu.add_cascade(
            label='Snittene vil først filtreres etter egendefinert filter og deretter stikkordfilteret')

        self.quiz_deactivate_mode_var.set('0')
        for r in self.quiz_deactivate_mode_list:
            button = tk.Radiobutton(box_label, text=r, variable=self.quiz_deactivate_mode_var, value=r, font=self.configs_tk['font'])
            button.pack(anchor='w')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_quiz_menu_checkbox_container(self):
        self.quiz_menu_checkbox_container = tk.Frame(self.quiz_menu_frame)
        self.quiz_menu_checkbox_container.pack(pady=10)

        self.create_quiz_module_box_container()
        self.create_quiz_order_box_container()
        self.create_quiz_deactivate_mode_container()

    def create_quiz_overview_container(self):
        quiz_overview_container = tk.Frame(self.quiz_menu_frame)
        quiz_overview_container.pack(pady=10)

        box_label = tk.LabelFrame(quiz_overview_container, text='SNITTOVERSIKT', font=self.configs_tk['font_b'],
                                  padx=32, pady=20, height=268, width=792)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Oversikt over snittutvalget (for stikkordfilter og egendefinert filter), samt andre innstillinger før "Start"')
        box_label_info_button.menu.add_cascade(label='Dersom det står "0 snitt" betyr det at det ikke finnes noen snitt for stikkordfilter, modulutvalg og egendefinert filter')

        self.quiz_slides_number_label = tk.Label(box_label, text=f'Snittutvalg: ? snitt',
                                                      font=self.configs_tk['font'], anchor='w', justify='left',
                                                      wraplength=self.configs_tk['w_length_menu'])
        self.quiz_slides_number_label.pack(anchor='w')
        self.quiz_filter_label = tk.Label(box_label, text=f'Stikkordfilter: Ingen',
                                            font=self.configs_tk['font'], anchor='w', justify='left',
                                            wraplength=self.configs_tk['w_length_menu'])
        self.quiz_filter_label.pack(anchor='w')
        self.quiz_module_label = tk.Label(box_label, text=f'Modulutvalg: ?',
                                              font=self.configs_tk['font'], anchor='w', justify='left',
                                              wraplength=self.configs_tk['w_length_menu'])
        self.quiz_module_label.pack(anchor='w')
        self.quiz_order_label = tk.Label(box_label, text=f'Rekkefølge: ?',
                                                    font=self.configs_tk['font'], anchor='w', justify='left',
                                                    wraplength=self.configs_tk['w_length_menu'])
        self.quiz_order_label.pack(anchor='w')
        self.quiz_deactivate_label = tk.Label(box_label, text=f'Egendefinert filter: ?',
                                            font=self.configs_tk['font'], anchor='w', justify='left',
                                            wraplength=self.configs_tk['w_length_menu'])
        self.quiz_deactivate_label.pack(anchor='w')
        update_button = tk.Button(box_label, text='Oppdater',
                                 bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                 height=1, width=10, command=lambda: self.on_check_quiz())
        update_button.pack(anchor='w')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_quiz_start_container(self):
        quiz_start_container = tk.Frame(self.quiz_menu_frame)
        quiz_start_container.pack(pady=10)

        start_button = tk.Button(quiz_start_container, text='START', command=lambda: self.on_start_quiz(),
                                 bg=self.configs_tk['color_green'], height=2, width=30, font=self.configs_tk['font_b'])
        start_button.grid(row=0, column=0, padx=5)

    def create_quiz_menu_frame(self):
        self.slides = []
        self.current_slide_index = 0
        self.filter_tags = []

        self.quiz_menu_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.quiz_menu_frame, anchor="n")
        self.quiz_menu_frame.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.quiz_menu_frame, 'PATOQUIZ')
        self.create_quiz_filter_container()
        self.create_quiz_menu_checkbox_container()
        self.create_quiz_overview_container()
        self.create_quiz_start_container()

    def on_check_quiz(self):
        included_module_tags = []
        for y in zip(self.quiz_module_list, self.quiz_check_label_module_vars):
            if y[1].get() == 1:
                included_module_tags.append(y[0])

        self.quiz_filter_tags = input_tags_to_list(self.quiz_text_input.get("1.0", 'end-1c'))
        if len(self.quiz_filter_tags) > 0:
            if self.quiz_filter_tags[0] != '':
                self.quiz_filter_label.configure(text=f'Filter: {self.quiz_filter_tags}')
            else:
                self.quiz_filter_label.configure(text=f'Filter: Ingen')
        else:
            self.quiz_filter_label.configure(text=f'Filter: Ingen')

        if len(included_module_tags) > 0:
            included_paths = []
            for pth in self.file_path_list:
                no_ext = pth.rsplit('.', 1)[0].lower()
                for yt in included_module_tags:
                    if yt.lower() in no_ext:
                        included_paths.append(pth)

            included_slides = 0
            excluded_slides = 0

            for pth in included_paths:
                file_json = open(pth, encoding='utf-8')
                try:
                    file_dict = json.load(file_json)
                except:
                    print(file_json)

                for q in range(1, len(file_dict) + 1):
                    slide = SlideEntry(file_dict[f'{pth.rsplit(".", 1)[0].rsplit("_", 1)[-1]}_{q}'])

                    if self.quiz_deactivate_mode_var.get() == 'Ja':
                        if slide.m8_status == "1":
                            if check_tag_in_string(slide, self.quiz_filter_tags):
                                included_slides += 1
                    else:
                        if check_tag_in_string(slide, self.quiz_filter_tags):
                            included_slides += 1

            all_tags = included_module_tags

            self.quiz_module_label.configure(text=f'Modulutvalg: {all_tags}')
            if included_slides > 0:
                self.quiz_slides_number_label.configure(
                    text=f'Snittutvalg: {included_slides} snitt')
            else:
                self.quiz_slides_number_label.configure(text=f'Snittutvalg: 0 snitt')
        else:
            self.quiz_module_label.configure(text=f'Modulutvalg: ?')
            self.quiz_slides_number_label.configure(text=f'Snittutvalg: ? snitt')
        if self.quiz_order_mode_var.get() != '0':
            self.quiz_order_label.configure(text=f'Rekkefølge: {self.quiz_order_mode_var.get()}')
        else:
            self.quiz_order_label.configure(text=f'Rekkefølge: ?')

        if self.quiz_deactivate_mode_var.get() != '0':
            self.quiz_deactivate_label.configure(text=f'Definert filter: {self.quiz_deactivate_mode_var.get()}')
        else:
            self.quiz_deactivate_label.configure(text=f'Definert filter: ?')

    def on_start_quiz(self):
        if self.quiz_order_mode_var.get() != '0' and self.quiz_deactivate_mode_var.get() != '0' and sum(
                [yv.get() for yv in self.quiz_check_label_module_vars]) > 0:

            included_module_tags = []
            for y in zip(self.quiz_module_list, self.quiz_check_label_module_vars):
                if y[1].get() == 1:
                    included_module_tags.append(y[0])

            included_paths = []
            for pth in self.file_path_list:
                no_ext = pth.rsplit('.', 1)[0].lower()
                for yt in included_module_tags:
                   if yt.lower() in no_ext:
                        included_paths.append(pth)

            included_slides = []
            self.quiz_filter_tags = input_tags_to_list(self.quiz_text_input.get("1.0", 'end-1c'))

            for pth in included_paths:
                file_json = open(pth, encoding='utf-8')
                try:
                    file_dict = json.load(file_json)
                    for q in range(1, len(file_dict) + 1):
                        slide = SlideEntry(file_dict[f'{pth.rsplit(".", 1)[0].rsplit("_", 1)[-1]}_{q}'])

                        if self.quiz_deactivate_mode_var.get() == 'Ja':
                            if slide.m8_status == "1":
                                if check_tag_in_string(slide, self.quiz_filter_tags):
                                    included_slides.append(slide)
                        else:
                            if check_tag_in_string(slide, self.quiz_filter_tags):
                                included_slides.append(slide)

                except:
                    print(file_json)

            if self.quiz_order_mode_var.get() == 'Tilfeldig':
                random.shuffle(included_slides)

            self.slides = included_slides
            if len(included_slides) > 0:
                self.create_quiz_slide_frame_from_menu()
                self.current_mode = 'PATOQUIZ'

                #self.state('normal')
                #self.geometry(f'{self.max_width // 2}x{self.max_height}')

    def create_quiz_menu_from_intro(self):
        self.intro_frame.destroy()
        self.create_quiz_menu_frame()

    def on_selectall_quiz(self, check_box_list):
        for i in check_box_list:
            i.select()

    def on_deselectall_quiz(self, check_box_list):
        for i in check_box_list:
            i.deselect()

    def create_quiz_slide_dock_info_container(self):
        dock_info_container = tk.Frame(self.quiz_slide_frame, height=40, width=790)
        dock_info_container.pack(anchor='w')

        self.progress_count = tk.StringVar()
        self.progress_count.set(f'Progresjon: {self.current_slide_index + 1} av {len(self.slides)}')
        progress_number = tk.Label(dock_info_container, textvariable=self.progress_count,
                                   font=self.configs_tk['font_ib'])
        progress_number.pack(side=tk.LEFT)

        self.correct_count = tk.StringVar()
        correct_percent = tk.Label(dock_info_container, textvariable=self.correct_count,
                                   font=self.configs_tk['font_ib'])
        correct_percent.pack(side=tk.RIGHT)

        dock_info_container.pack_propagate(False)

    def create_quiz_slide_dock_button_container(self):
        button_container = tk.Frame(self.quiz_slide_frame)
        button_container.pack(anchor='center')

        previous_button = tk.Button(button_container, text='<', command=lambda: self.on_previous_quiz(),
                                    bg=self.configs_tk['color_white'], height=1, width=7,
                                    font=self.configs_tk['font_b'])
        previous_button.grid(row=0, column=0, padx=5)
        self.quiz_answer_button = tk.Button(button_container, text='FASIT', command=lambda: self.on_show_quiz(),
                                            bg=self.configs_tk['color_orange'], height=1, width=14,
                                            font=self.configs_tk['font_b'])
        self.quiz_answer_button.grid(row=0, column=1, padx=5)
        next_button = tk.Button(button_container, text='>', command=lambda: self.on_next_quiz(),
                                bg=self.configs_tk['color_white'], height=1, width=7, font=self.configs_tk['font_b'])
        next_button.grid(row=0, column=2, padx=5)

        #self.answer_label = tk.Label(button_container, text='', font=self.configs_tk['font_b'])
        #self.answer_label.grid(row=1, column=1, padx=5)

    def create_quiz_slide_extra_button_container(self):
        self.quiz_slide_extra_button_container = tk.Frame(self.quiz_slide_frame)
        self.quiz_slide_extra_button_container.pack(anchor='center', pady=10)

        if len(self.slides[self.current_slide_index].extra_slide_id) != 0:

            org_button = tk.Button(self.quiz_slide_extra_button_container, text=f'H&E', command=lambda:self.on_link_button_quiz(self.slides[self.current_slide_index].slide_link), font=self.configs_tk['font_b'],
                                   height=1, width=14, bg='white')
            org_button.grid(row=0, column=0, padx=5)

            self.extra_link_vars = []

            for r in self.slides[self.current_slide_index].extra_slide_id:
                self.extra_link_vars.append(tk.StringVar())
                self.extra_link_vars[-1] = r[0]
                button = tk.Button(self.quiz_slide_extra_button_container, text=f'{r[1]}', command=lambda x=r[0]:self.on_link_button_quiz(x), bg='white', font=self.configs_tk['font_b'], height=1, width=14)
                button.grid(row=0, column=len(self.extra_link_vars), padx=5)

    def create_text_container(self, frame):
        self.text_container = tk.Frame(frame)
        self.text_container.pack(anchor='w')

        self.driver.get(self.slides[self.current_slide_index].slide_link)

        self.slide_answer_label = tk.Label(self.text_container, text='', font=self.configs_tk['font_b'], pady=10)
        self.slide_answer_label.pack()

        history_label = tk.Label(self.text_container, text='Sykehistorie:', font=self.configs_tk['font_b'],
                              justify='left', wraplength=self.configs_tk['w_length'], pady=10)
        history_label.pack(anchor='w')

        history_text_label = tk.Label(self.text_container, text=self.slides[self.current_slide_index].slide_text,
                                   font=self.configs_tk['font'], justify='left',
                                   wraplength=self.configs_tk['w_length'])
        history_text_label.pack(anchor='w')

        self.comment_label = tk.Label(self.text_container, text='', font=self.configs_tk['font_b'], justify='left',
                                   wraplength=self.configs_tk['w_length'], pady=10)
        self.comment_label.pack(anchor='w')

        self.comment_text_label = tk.Label(self.text_container, text='',
                                        font=self.configs_tk['font'], justify='left',
                                        wraplength=self.configs_tk['w_length'])
        self.comment_text_label.pack(anchor='w')

        self.goal_label = tk.Label(self.text_container, text='', font=self.configs_tk['font_b'], justify='left',
                                wraplength=self.configs_tk['w_length'], pady=10)
        self.goal_label.pack(anchor='w')

        self.goal_text_label = tk.Label(self.text_container, text='',
                                     font=self.configs_tk['font'], justify='left',
                                     wraplength=self.configs_tk['w_length'])
        self.goal_text_label.pack(anchor='w')

        self.notes_label = tk.Label(self.text_container, text='', font=self.configs_tk['font_ib'], justify='left',
                                 wraplength=self.configs_tk['w_length'], pady=10)
        self.notes_label.pack(anchor='w')

        self.notes_explanation_label = tk.Label(self.text_container, text='', font=self.configs_tk['font_i'], justify='left',
                                          wraplength=self.configs_tk['w_length'])
        self.notes_explanation_label.pack(anchor='w')

    def create_quiz_slide_frame(self):
        self.quiz_slide_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.quiz_slide_frame.pack(anchor='w')
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.quiz_slide_frame, anchor="n")
        self.quiz_slide_frame.bind('<Configure>',
                                    lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_service = Service(ChromeDriverManager().install())
        chrome_service.creationflags = CREATE_NO_WINDOW
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        self.create_subtitle_info_container(self.quiz_slide_frame, 'PATOQUIZ')
        self.create_quiz_slide_dock_info_container()
        self.create_quiz_slide_dock_button_container()
        self.create_quiz_slide_extra_button_container()
        self.create_text_container(self.quiz_slide_frame)

    def create_quiz_slide_frame_from_menu(self):
        self.quiz_menu_frame.destroy()
        self.create_quiz_slide_frame()

    def on_link_button_quiz(self, link):
        self.driver.get(link)

    def on_show_quiz(self):
        self.slide_answer_label.configure(text=self.slides[self.current_slide_index].slide_set)

        self.quiz_answer_button.configure(text='NESTE', bg=self.configs_tk['color_green'],
                                          command=lambda: self.on_next_quiz())

        self.comment_label.configure(text='Kommentar:')
        self.comment_text_label.configure(text=self.slides[self.current_slide_index].slide_comment)

        self.goal_label.configure(text='Læringsmål:')
        self.goal_text_label.configure(text=self.slides[self.current_slide_index].slide_goal)

        self.notes_label.configure(text='Egne notater:')
        self.notes_explanation_label.configure(
            text='Trykk på det hvite og skriv med tastatur. Teksten i boksen lagres etter trykk av "Neste", "<", ">" eller "Hjem".')

        self.notes = tk.Text(self.quiz_slide_frame, font=self.configs_tk['font'], borderwidth=0, wrap='word', height=10)
        self.notes.insert(1.0, self.slides[self.current_slide_index].slide_notes)
        self.notes.pack(anchor='w')

    def save_notes(self):
        try:
            if self.slides[self.current_slide_index].slide_notes != self.notes.get("1.0", 'end-1c'):
                new_notes = self.notes.get("1.0", 'end-1c')
                self.slides[self.current_slide_index].slide_notes = new_notes
                self.slides[self.current_slide_index].modify_json()
        except:
            pass

    def on_next_quiz(self):
        try:
            self.save_notes()
            self.notes.destroy()
        except:
            pass

        self.current_slide_index += 1

        if self.current_slide_index >= len(self.slides):
            self.quiz_slide_frame.destroy()
            self.create_quiz_menu_frame()
            self.driver.quit()
        else:
            self.quiz_answer_button.configure(text='FASIT', command=lambda: self.on_show_quiz(), bg=self.configs_tk['color_orange'])
            self.slide_answer_label.configure(text='')

            self.quiz_slide_extra_button_container.destroy()
            self.text_container.destroy()

            self.create_quiz_slide_extra_button_container()
            self.create_text_container(self.quiz_slide_frame)

            self.progress_count.set(f'Progresjon: {self.current_slide_index + 1} av {len(self.slides)}')

    def on_previous_quiz(self):
        try:
            self.save_notes()
            self.notes.destroy()
        except:
            pass

        self.current_slide_index -= 1

        if self.current_slide_index >= 0:
            self.quiz_answer_button.configure(text='FASIT', command=lambda: self.on_show_quiz(), bg=self.configs_tk['color_orange'])
            self.slide_answer_label.configure(text='')

            self.quiz_slide_extra_button_container.destroy()
            self.text_container.destroy()

            self.create_quiz_slide_extra_button_container()
            self.create_text_container(self.quiz_slide_frame)

            self.progress_count.set(f'Progresjon: {self.current_slide_index + 1} av {len(self.slides)}')
        else:
            self.quiz_slide_frame.destroy()
            self.create_quiz_menu_frame()
            self.driver.quit()

    def create_deactivate_m3_list_container(self, title):
        module_list_container = tk.Frame(self.deactivate_menu_frame)
        module_list_container.pack(pady=10)

        self.deactivate_m3_check_label_module = []
        self.deactivate_m3_check_label_module_vars = []

        box_label = tk.LabelFrame(module_list_container, text='MODUL 3', font=self.configs_tk['font_b'], padx=32, pady=20, width=792, height=220)#, bg='blue')
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'],
                                              relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w', pady=5)
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label=f'Valg av snitt for {title}. Bruk scrollbaren for å se hele listen')

        check_canvas = tk.Canvas(box_label)#, bg='green') #canvas reduces height(padding) from the top, button has to be sw
        check_canvas.pack(anchor='nw', side=tk.LEFT, expand=True, fill=tk.X)

        scrollbar = tk.Scrollbar(box_label, orient=tk.VERTICAL, command=check_canvas.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT, anchor='nw')
        check_canvas.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=check_canvas.yview)
        box_label.bind('<Configure>', lambda e: check_canvas.configure(scrollregion=check_canvas.bbox("all")))

        check_subcontainer = tk.Frame(check_canvas)#, bg='red') #canvas reduces height(padding) from the top, button has to be sw
        check_subcontainer.pack(anchor='nw')

        pth = f'{title}_m{title.rsplit(' ', 1)[-1]}.json'
        file_json = open(pth, encoding='utf-8')

        try:
            file_dict = json.load(file_json)
            for q in range(1, len(file_dict) + 1):
                slide = SlideEntry(file_dict[f'{pth.rsplit(".", 1)[0].rsplit("_", 1)[-1]}_{q}'])
                slide_name = slide.slide_set

                self.deactivate_m3_check_label_module_vars.append(tk.IntVar())
                check_label = tk.Checkbutton(check_subcontainer, text=slide_name,
                                             variable=self.deactivate_m3_check_label_module_vars[-1],
                                             font=self.configs_tk['font'])
                self.deactivate_m3_check_label_module.append(check_label)
                check_label.pack(anchor='w')

                if slide.m8_status == "1":
                    self.deactivate_m3_check_label_module[-1].select()
        except:
            print(file_json)

        select_all_button = tk.Button(box_label, text='Velg alle',
                                      command=lambda: self.on_selectall_quiz(self.deactivate_m3_check_label_module),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        select_all_button.pack(anchor='w')
        remove_all_button = tk.Button(box_label, text='Fjern alle',
                                      command=lambda: self.on_deselectall_quiz(self.deactivate_m3_check_label_module),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        remove_all_button.pack(anchor='w')

        check_canvas.create_window((0, 0), window=check_subcontainer, anchor='nw')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_deactivate_m6_list_container(self, title):
        module_list_container = tk.Frame(self.deactivate_menu_frame)
        module_list_container.pack(pady=10)

        self.deactivate_m6_check_label_module = []
        self.deactivate_m6_check_label_module_vars = []

        box_label = tk.LabelFrame(module_list_container, text='MODUL 6', font=self.configs_tk['font_b'], padx=32, pady=20, width=792, height=220)#, bg='blue')
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'],
                                              relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w', pady=5)
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label=f'Valg av snitt for {title}. Bruk scrollbaren for å se hele listen')

        check_canvas = tk.Canvas(box_label)#, bg='green') #canvas reduces height(padding) from the top, button has to be sw
        check_canvas.pack(anchor='nw', side=tk.LEFT, expand=True, fill=tk.X)

        scrollbar = tk.Scrollbar(box_label, orient=tk.VERTICAL, command=check_canvas.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT, anchor='nw')
        check_canvas.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=check_canvas.yview)
        box_label.bind('<Configure>', lambda e: check_canvas.configure(scrollregion=check_canvas.bbox("all")))

        check_subcontainer = tk.Frame(check_canvas)#, bg='red') #canvas reduces height(padding) from the top, button has to be sw
        check_subcontainer.pack(anchor='nw')

        pth = f'{title}_m{title.rsplit(' ', 1)[-1]}.json'
        file_json = open(pth, encoding='utf-8')

        try:
            file_dict = json.load(file_json)
            for q in range(1, len(file_dict) + 1):
                slide = SlideEntry(file_dict[f'{pth.rsplit(".", 1)[0].rsplit("_", 1)[-1]}_{q}'])
                slide_name = slide.slide_set

                self.deactivate_m6_check_label_module_vars.append(tk.IntVar())
                check_label = tk.Checkbutton(check_subcontainer, text=slide_name,
                                             variable=self.deactivate_m6_check_label_module_vars[-1],
                                             font=self.configs_tk['font'])
                self.deactivate_m6_check_label_module.append(check_label)
                check_label.pack(anchor='w')

                if slide.m8_status == "1":
                    self.deactivate_m6_check_label_module[-1].select()
        except:
            print(file_json)

        select_all_button = tk.Button(box_label, text='Velg alle',
                                      command=lambda: self.on_selectall_quiz(self.deactivate_m6_check_label_module),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        select_all_button.pack(anchor='w')
        remove_all_button = tk.Button(box_label, text='Fjern alle',
                                      command=lambda: self.on_deselectall_quiz(self.deactivate_m6_check_label_module),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        remove_all_button.pack(anchor='w')

        check_canvas.create_window((0, 0), window=check_subcontainer, anchor='nw')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_deactivate_m8_list_container(self, title):
        module_list_container = tk.Frame(self.deactivate_menu_frame)
        module_list_container.pack(pady=10)

        self.deactivate_m8_check_label_module = []
        self.deactivate_m8_check_label_module_vars = []

        box_label = tk.LabelFrame(module_list_container, text='MODUL 8', font=self.configs_tk['font_b'], padx=32, pady=20, width=792, height=220)#, bg='blue')
        box_label.pack()

        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'],
                                              relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w', pady=5)
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label=f'Valg av snitt for {title}. Bruk scrollbaren for å se hele listen')

        check_canvas = tk.Canvas(box_label)#, bg='green') #canvas reduces height(padding) from the top, button has to be sw
        check_canvas.pack(anchor='nw', side=tk.LEFT, expand=True, fill=tk.X)

        scrollbar = tk.Scrollbar(box_label, orient=tk.VERTICAL, command=check_canvas.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT, anchor='nw')
        check_canvas.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=check_canvas.yview)
        box_label.bind('<Configure>', lambda e: check_canvas.configure(scrollregion=check_canvas.bbox("all")))

        check_subcontainer = tk.Frame(check_canvas)#, bg='red') #canvas reduces height(padding) from the top, button has to be sw
        check_subcontainer.pack(anchor='nw')

        pth = f'{title}_m{title.rsplit(' ', 1)[-1]}.json'
        file_json = open(pth, encoding='utf-8')

        try:
            file_dict = json.load(file_json)
            for q in range(1, len(file_dict) + 1):
                slide = SlideEntry(file_dict[f'{pth.rsplit(".", 1)[0].rsplit("_", 1)[-1]}_{q}'])
                slide_name = slide.slide_set

                self.deactivate_m8_check_label_module_vars.append(tk.IntVar())
                check_label = tk.Checkbutton(check_subcontainer, text=slide_name,
                                             variable=self.deactivate_m8_check_label_module_vars[-1],
                                             font=self.configs_tk['font'])
                self.deactivate_m8_check_label_module.append(check_label)
                check_label.pack(anchor='w')

                if slide.m8_status == "1":
                    self.deactivate_m8_check_label_module[-1].select()
        except:
            print(file_json)

        select_all_button = tk.Button(box_label, text='Velg alle',
                                      command=lambda: self.on_selectall_quiz(self.deactivate_m8_check_label_module),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        select_all_button.pack(anchor='w')
        remove_all_button = tk.Button(box_label, text='Fjern alle',
                                      command=lambda: self.on_deselectall_quiz(self.deactivate_m8_check_label_module),
                                      bg=self.configs_tk['color_white'], font=self.configs_tk['font_i'],
                                      height=1, width=10)
        remove_all_button.pack(anchor='w')

        check_canvas.create_window((0, 0), window=check_subcontainer, anchor='nw')
        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_deactivate_overview_container(self):
        deactivate_overview_container = tk.Frame(self.deactivate_menu_frame)
        deactivate_overview_container.pack(pady=10)

        box_label = tk.LabelFrame(deactivate_overview_container, text='SNITTOVERSIKT', font=self.configs_tk['font_b'],
                                  padx=32, pady=20, height=170, width=792)
        box_label.pack()
        box_label_info_button = tk.Menubutton(box_label, text="Info", font=self.configs_tk['font_i'],
                                              bg=self.configs_tk['color_grey'], fg=self.configs_tk['color_white'], relief='raised', height=1,
                                              width=10)
        box_label_info_button.pack(anchor='w')
        box_label_info_button.menu = tk.Menu(box_label_info_button, tearoff=0)
        box_label_info_button["menu"] = box_label_info_button.menu
        box_label_info_button.menu.add_cascade(label='Oversikt over snittutvalget for egendefinert filter')
        box_label_info_button.menu.add_cascade(label='Vil aktiveres når man velger "Ja" i for Definert filter i PatoQuiz')
        box_label_info_button.menu.add_cascade(label='Trykk på "LAGRE" for å lagre snittutvalget')

        self.deactivate_m3_number_label = tk.Label(box_label, text=f'Utvalg Modul 3: ? snitt',
                                                      font=self.configs_tk['font'], anchor='w', justify='left',
                                                      wraplength=self.configs_tk['w_length_menu'])
        self.deactivate_m3_number_label.pack(anchor='w')
        self.deactivate_m6_number_label = tk.Label(box_label, text=f'Utvalg Modul 6: ? snitt',
                                            font=self.configs_tk['font'], anchor='w', justify='left',
                                            wraplength=self.configs_tk['w_length_menu'])
        self.deactivate_m6_number_label.pack(anchor='w')
        self.deactivate_m8_number_label = tk.Label(box_label, text=f'Utvalg Modul 8: ? snitt',
                                              font=self.configs_tk['font'], anchor='w', justify='left',
                                              wraplength=self.configs_tk['w_length_menu'])
        self.deactivate_m8_number_label.pack(anchor='w')

        box_label.pack_propagate(False)  # makes height and width in labelframe active

    def create_deactivate_save_container(self):
        deactivate_save_container = tk.Frame(self.deactivate_menu_frame)
        deactivate_save_container.pack(pady=10)

        save_button = tk.Button(deactivate_save_container, text='LAGRE', command=lambda: self.on_save_deactivate(),
                                 bg=self.configs_tk['color_green'], height=2, width=30, font=self.configs_tk['font_b'])
        save_button.grid(row=0, column=0, padx=5)

    def create_deactivate_menu_frame(self):
        self.deactivate_menu_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.deactivate_menu_frame, anchor="n")
        self.deactivate_menu_frame.bind('<Configure>',
                                        lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.current_mode = 'EGENDEFINERT FILTER'
        self.create_subtitle_info_container(self.deactivate_menu_frame, 'EGENDEFINERT FILTER')
        self.create_deactivate_m3_list_container('Modul 3')
        self.create_deactivate_m6_list_container('Modul 6')
        self.create_deactivate_m8_list_container('Modul 8')
        self.create_deactivate_overview_container()
        self.create_deactivate_save_container()

    def create_deactivate_menu_from_intro(self):
        self.intro_frame.destroy()
        self.create_deactivate_menu_frame()

    def on_save_deactivate(self):
        included_slides = []
        included_m3 = 0
        excluded_m3 = 0
        included_m6 = 0
        excluded_m6 = 0
        included_m8 = 0
        excluded_m8 = 0

        for f in zip(self.deactivate_m3_check_label_module, self.deactivate_m3_check_label_module_vars):
            if f[1].get() == 1:
                included_slides.append(f[0].cget('text'))
                included_m3 += 1
            else:
                excluded_m3 += 1

        for e in zip(self.deactivate_m6_check_label_module, self.deactivate_m6_check_label_module_vars):
            if e[1].get() == 1:
                included_slides.append(e[0].cget('text'))
                included_m6 += 1
            else:
                excluded_m6 += 1

        for y in zip(self.deactivate_m8_check_label_module, self.deactivate_m8_check_label_module_vars):
            if y[1].get() == 1:
                included_slides.append(y[0].cget('text'))
                included_m8 += 1
            else:
                excluded_m8 += 1

        #print(included_slides)

        for pth in self.file_path_list:
            try:
                with open(pth, "r", encoding="utf8") as file_json:
                    file_dict = json.load(file_json)

                for l in file_dict:
                    if file_dict[l]['slide_set'] in included_slides:
                        file_dict[l]['m8_status'] = '1'
                    else:
                        file_dict[l]['m8_status'] = '0'

                with open(pth, "w", encoding="utf8") as file_json:
                    json.dump(file_dict, file_json)
            except:
                print(pth)

        self.deactivate_m3_number_label.configure(text=f'Utvalg Modul 3: {included_m3} av {included_m3 + excluded_m3} snitt')
        self.deactivate_m6_number_label.configure(text=f'Utvalg Modul 6: {included_m6} av {included_m6 + excluded_m6} snitt')
        self.deactivate_m8_number_label.configure(text=f'Utvalg Modul 8: {included_m8} av {included_m8 + excluded_m8} snitt')

    def create_about_info_container(self, frame, title, text):
        about_info_container = tk.Frame(frame)
        about_info_container.pack(anchor='w', pady=10)

        about_title_label = tk.Label(about_info_container,
                                     text=title, font=self.configs_tk['font_b'], justify='left',
                                     wraplength=self.configs_tk['w_length'])
        about_title_label.pack(anchor='w')
        about_text_label = tk.Label(about_info_container, text=text, font=self.configs_tk['font'], justify='left',
                                    wraplength=self.configs_tk['w_length'])
        about_text_label.pack(anchor='w')

    def create_link_info_container(self, frame, title, link_list):
        link_info_container = tk.Frame(frame)
        link_info_container.pack(anchor='w', pady=10)
        sources_text = tk.Label(link_info_container,
                                text=title, font=self.configs_tk['font_b'], justify='left',
                                wraplength=self.configs_tk['w_length'])
        sources_text.pack(anchor='w')
        sources_link = tk.Text(link_info_container, font=self.configs_tk['font'], height=len(link_list), borderwidth=0,
                               width=88)
        for l in link_list:
            sources_link.insert(1.0, f'{l}\n')
        sources_link.configure(state='disabled')
        sources_link.pack(anchor='w')

    def create_sources_frame(self):
        self.sources_frame = tk.Frame(self.main_canvas, pady=10, padx=80)
        self.main_canvas.create_window((self.max_width // 2, 0), window=self.sources_frame, anchor="n")
        self.sources_frame.bind('<Configure>',
                                lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

        self.create_subtitle_info_container(self.sources_frame, 'INFO OG KILDER')

        self.create_about_info_container(self.sources_frame, 'OM PROGRAMMET',
                                         '''Programmet har enkelte begrensninger man bør være klar over.\n• Programmet bruker internett og forutsetter oppdatert versjon av Chrome.\n• Når PatoQuiz kjører må ikke Chrome-vinduet med patosnittet lukkes da vinduet vil oppdateres automatisk etter man går til neste/forrige snitt.\n• Programmet forutsetter at UiO ikke endrer på linkene til patologisiden sin.\n• Tidligere har det vært problemer med krasjing av program etter Chrome oppdateringer. Dette problemet burde nå være fikset ved at nyeste versjon av chromedriver lastes ned automatisk ved oppdateringer''')
        self.create_about_info_container(self.sources_frame, 'OM MEG',
                                         'Hei, jeg heter Sigurd Z. Zha og har vært medisin- og forskerlinjestudent ved UiO 2017-2024. Programmet ble laget for å lettere trene på patologi. Synes det var kult at mange på kull V18 fikk nytte av programmet, så har nå laget en oppdatert versjon med forbedringer. Er nå ferdig lege, men vedlikeholder programmet på fritiden. Disclaimer: Det er UiO som eier rettighetene til alle patologisnittene. Donasjoner kan gå til MedHum.\n\nTa gjerne kontakt med meg på Facebook eller på mail (sigzha@gmail.com) dersom det er noe du lurer på')
        self.create_link_info_container(self.sources_frame, 'PATOLOGISNITT', [
            'https://studmed.uio.no/elaring/fag/patologi/index.shtml'])
        self.create_link_info_container(self.sources_frame, 'KILDEKODE', ['https://github.com/shigurd/UiOPato.git'])

    def create_sources_from_intro(self):
        self.intro_frame.destroy()
        self.create_sources_frame()

    def quit_driver_and_program(self):
        try:
            self.driver.quit()
            self.destroy()
        except:
            self.destroy()

if __name__ == '__main__':
    #activate pip_only
    #pyinstaller main.spec
    os.chdir(os.path.join(os.path.dirname(sys.argv[0]), "lib"))
    chromedriver_autoinstaller.install(cwd=True, path="lib")

    question_set_json_pths = ['Modul 3_m3.json', 'Modul 6_m6.json', 'Modul 8_m8.json']

    app = QuizApp(question_set_json_pths)
    app.tkraise()
    app.protocol("WM_DELETE_WINDOW", app.quit_driver_and_program)
    app.mainloop()


