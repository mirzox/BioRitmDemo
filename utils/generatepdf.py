import os
from datetime import datetime

from django.conf import settings
from fpdf import FPDF

from service.models import Category

# pdf = FPDF('P', 'mm', 'A4')

C1 = ["Клинические исследования", "Электролиты", "Онкомаркеры ИФА исследования", "Забор на бак. Посев из",
      "СЕРОЛОГИЯ", "ОНКОМАРКЕРЫ"

      ]
C2 = ["Биохимический спектр", "Гепатит панель", "Коагулограмма",
      "Дополнительные Биохимические Исследование", "БИОХИМИЯ КРОВИ",
      ]
C3 = ["Липидный спектр", "TORCH инфекции", "Паразиты ИФА иследования",
      "Инфекции ПЦР – качеств.", "Инфекции ПЦР – колич."]
C4 = ["Ревматоидная панель", "Гормоны Щитовидной железы",
      "Половые Гормоны", "ГОРМОНЫ В КРОВИ", "Covid – 19 (Эспресс тест)"]


class PDF(FPDF):
    utils_path = os.path.join(settings.BASE_DIR, "utils/")

    def cell_(self, pdf_: FPDF, w=None, h=None, txt="", border=0, ln=0, align="", fill=False, link="",
              center=False, markdown=False, i_font=False, font="PTSans", type_="", size=14, move=False,
              m_w=10, m_h=None, m_ln=0):
        if i_font:
            pdf_.set_font(font, type_, size)
        if move:
            pdf_.cell(m_w, m_h, ln=m_ln)
        pdf_.cell(w, h, txt, border, ln, align, fill, link)


def height(data):
    # temp = max([len(i) for i in data])
    norm = max([len(i.split('\n')) for i in data])
    if norm in [1, 2]:
        return 7
    else:
        return 3.5 * norm
    # if temp < 40:
    #     return 10
    # elif temp // 2 < 40:
    #     return 20
    # else:
    #     return 20


def add_header(pdf_: PDF, logo_path):
    pdf_.add_page()
    pdf_.image(f'{logo_path}/images/logo.png', 10, 5, 40, 18)
    pdf_.set_fill_color(0, 0, 0)
    pdf_.cell_(pdf_, 191, 0.5, border=1, fill=True, ln=1, move=True, m_w=1, m_h=15, m_ln=1)
    pdf_.cell(1, 5, ln=1)


font_color = []


def set_fill_color(pdf_: PDF, category: str):
    if category in C1:
        pdf_.set_fill_color(75, 191, 105)
    elif category in C2:
        pdf_.set_fill_color(108, 108, 108)
    elif category in C3:
        pdf_.set_fill_color(102, 186, 230)
    elif category in C4:
        pdf_.set_fill_color(223, 107, 108)
    else:
        pdf_.set_fill_color(255, 102, 0)


def get_pdf(data: dict, file_name: list):
    pdf = PDF('P', 'mm', 'A4')

    utils_path = pdf.utils_path
    pdf.add_page()
    pdf.add_font('PTSans', '', f'{str(utils_path)}fonts/PTSans-Regular.ttf', uni=True)
    pdf.add_font('PTSans', 'B', f'{str(utils_path)}fonts/PTSans-Bold.ttf', uni=True)

    pdf.image(f'{str(utils_path)}/images/logo.png', 10, 5, 40, 18)
    pdf.cell_(pdf, 70, 4, 'OOO "BIO-RITM MEDICAL SERVICE"', i_font=True, type_="B", size=7, move=True, m_w=42)
    pdf.cell_(pdf, 70, 4, 'Используем реагенты и оборудования компаний', ln=1, move=True, m_w=25)
    pdf.cell_(pdf, 70, 3, 'Адрес: Юнус-абад 19кв дом 4/5', i_font=True, type_="", size=7, move=True, m_w=42)

    pdf.image(f'{str(utils_path)}/images/3.png', 152, 14, 50, 11)
    pdf.cell(1, 3, ln=1)

    pdf.cell_(pdf, 70, 3, 'Тел:(95)144 40 33 (71)22247 27', ln=1, move=True, m_w=42)
    pdf.cell_(pdf, 70, 3, 'Эл.почта: bioritm.lab@mail.ru', ln=1, move=True, m_w=42)

    pdf.cell_(pdf, 191, 0.5, border=1, fill=True, ln=1, move=True, m_w=1, m_h=10, m_ln=1)

    # set patient information
    p_i = data.pop('patient_id')
    gender = "Мужчина" if p_i["gender"] == "male" else "Женщина"
    pdf.cell_(pdf, 13, 15, "Имя:", i_font=True, type_="B", size=14)
    pdf.cell_(pdf, 80, 15, p_i['firstname'], i_font=True, type_="", size=14)
    pdf.cell_(pdf, 13, 15, "Пол:", i_font=True, type_="B", size=14)
    pdf.cell_(pdf, 80, 15, gender, i_font=True, type_="", size=14, ln=1)

    pdf.cell_(pdf, 24, 6, "Фамилия:", i_font=True, type_="B", size=14)
    pdf.cell_(pdf, 69, 6, p_i['secondname'], i_font=True, type_="", size=14)
    pdf.cell_(pdf, 35, 6, "Год рождения:", i_font=True, type_="B", size=14)
    pdf.cell_(pdf, 60, 6, f"{p_i['birth']}", i_font=True, type_="", size=14)

    pdf.cell_(pdf, 191, 0, border=1, fill=True, ln=1, move=True, m_w=1, m_h=10, m_ln=1)

    pdf.cell_(pdf, 69, 17, "Дата и время взятия образца:", i_font=True, type_="B", size=14)
    pdf.cell_(pdf, 50, 17, f"{datetime.fromisoformat(p_i['timestamp'].split('.')[0]).strftime('%d.%m.%Y %H-%M-%S')}", i_font=True, type_="", size=14, ln=1)

    pdf.cell(191, 0.5, '_ ' * 57, ln=1)
    for iter_, j in enumerate(data['results'].items()):
        l_h = 35
        i, j = j
        if not Category.objects.get(name=i).is_continuous:
        # if i in ["УЗИ", "Консультации Врачей", "Услуги Гинеколога"]:
            continue
        for row in data:
            l_h += height(row)
            l_h += 1
        y = pdf.y
        temp = y+l_h
        if temp >= 290:
            add_header(pdf, utils_path)
            # print("WOINFE")
            # h = 297-y-25
            # print(h)
            # pdf.cell(50, h, ln=1)
        else:
            pdf.cell(1, 5, ln=1)
            if iter_ > 0:
                add_header(pdf, utils_path)
        set_fill_color(pdf, i)

        # pdf.set_font('PTSans', 'B', 14)
        pdf.set_text_color(255, 255, 255)

        pdf.cell_(pdf, 191, 10, i, align="C", fill=True, ln=1, i_font=True, type_="B")

        pdf.set_text_color(31, 26, 23)

        pdf.cell_(pdf, 80, 15, "Название/показатель", align="L")
        pdf.cell_(pdf, 64, 15, "Норма", align="L")
        pdf.cell_(pdf, 47, 15, "Результат", align="L", ln=1)
        # pdf.cell(10, ln=1)

        pdf.set_fill_color(245, 255, 243)
        for col in j:
            for row in col:
                line_height = height([row["param_id"]["name"], row["param_id"]["norm"], row["res"]])
                pdf.set_font('PTSans', '', 11)
                pdf.multi_cell(80, line_height, row["param_id"]["name"], max_line_height=pdf.font_size, ln=3, fill=True)
                pdf.set_font('PTSans', '', 9)
                pdf.multi_cell(64, line_height, row["param_id"]["norm"], max_line_height=pdf.font_size, align="L", ln=3,
                               fill=True)
                pdf.set_font('PTSans', '', 9)
                pdf.multi_cell(47, line_height, row["res"], max_line_height=pdf.font_size, ln=3, fill=True)
                pdf.ln(line_height)
                pdf.cell(10, 2, ln=1)
                if pdf.y + 30 >= 295:
                    add_header(pdf, utils_path)
                    pdf.set_fill_color(245, 255, 243)
    pdf.set_font('PTSans', '', 10)
    pdf.set_y(240)
    pdf.cell(1, 1, ln=1)
    pdf.cell(10, 5)
    pdf.multi_cell(170, 5, "Интерпретацию полученных результатов "
                            "проводит врач в совокупности с данными анамнеза, клиническими данными и "
                            "результатами других диагностических исследований. ", ln=1)
    pdf.cell(190, 12, ln=1)
    pdf.cell(70, 10)
    pdf.cell_(pdf, 63, 10, "Заведующая лабораторией:", i_font=True, type_="B", size=14)
    pdf.cell_(pdf, 50, 10, "Ишанходжаева Д.", i_font=True, type_="", size=14)
    output_path = os.path.join(settings.BASE_DIR, 'mediafiles/results/{}_{}_{}.pdf'.format(file_name[0], file_name[1], file_name[2]))
    pdf.output(output_path)
    return output_path.replace(f"{str(settings.BASE_DIR)}/mediafiles", "media")


# pdf.set_font('PTSans', '', 7)
# pdf.cell(42)
# pdf.set_font('PTSans', 'B', 7)
# pdf.cell(70, 4, 'OOO "BIO-RITM MEDICAL SERVICE"')

# pdf.set_font('PTSans', 'B', 7)
# pdf.cell(25)
# pdf.cell(70, 4, 'Используем реагенты и оборудования компаний', ln=1)

# pdf.set_font('PTSans', '', 7)
# pdf.cell(42)
# pdf.cell(70, 3, 'Адрес: Юнус-абад 19кв дом 4/5')

# pdf.image('3.png', 152, 14, 50, 11)
# pdf.cell(1, 3, ln=1)

# pdf.cell(42)
# pdf.cell(70, 3, 'Тел:(95)144 40 33 (71)22247 27', ln=1)

# pdf.cell(42)
# pdf.cell(70, 3, 'Эл.почта: bioritm.lab@mail.ru', ln=1)

# pdf.cell(42)
# pdf.cell(100, 10, "Адрес: Юнус-абад 19кв дом 4//5", ln=1)

# pdf.cell(1, 10, ln=1)
# pdf.cell(191, 0.5, border=1, fill=1, ln=1)

# pdf.set_font('PTSans', 'B', 14)
# pdf.cell(13, 15, "Имя:")

# pdf.set_font('PTSans', '', 14)
# pdf.cell(80, 15, 'Мирзохид')

# pdf.set_font('PTSans', 'B', 14)
# pdf.cell(13, 15, "Пол:")

# pdf.set_font('PTSans', '', 14)
# pdf.cell(80, 15, 'Мужчина', ln=1)

# pdf.set_font('PTSans', 'B', 14)
# pdf.cell(24, 6, "Фамилия:")
# pdf.set_font('PTSans', '', 14)
# pdf.cell(69, 6, 'Абдурахматов')

# pdf.set_font('PTSans', 'B', 14)
# pdf.cell(35, 6, "Год рождения:")
# pdf.set_font('PTSans', '', 14)
# pdf.cell(60, 6, '2001')

# pdf.cell(1, 10, ln=1)
# pdf.cell(191, 0, border=1, fill=1, ln=1)

# pdf.set_font('PTSans', 'B', 14)
# pdf.cell(69, 17, "Дата и время взятия образца:")

# pdf.cell(50, 17, "20.03.2022 15:01:00", ln=1)
# pdf.set_font('PTSans', '', 14)

# pdf.cell(191, 0.5, '_ ' * 57, ln=1)
# pdf.cell(1, 10, ln=1)

# pdf.set_fill_color(75, 191, 105)
# pdf.set_font('PTSans', 'B', 14)
# pdf.set_text_color(255, 255, 255)
#
# pdf.cell(191, 10, 'ПЦР ИССЛЕДОВАНИЯ', align="C", fill=1, ln=1)

# pdf.output('1.pdf')
