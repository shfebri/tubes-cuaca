import xml.etree.ElementTree as ET
from tkinter import filedialog
import tkinter as tk
import os


def translate_wd(wd):
    if wd == 'N':
        return 'North'
    elif wd == 'NNE':
        return 'North-Northeast'
    elif wd == 'NE':
        return 'Northeast'
    elif wd == 'ENE':
        return 'East-Northeast'
    elif wd == 'E':
        return 'East'
    elif wd == 'ESE':
        return 'East-Southeast'
    elif wd == 'SE':
        return 'Southeast'
    elif wd == 'SSE':
        return 'South-Southeast'
    elif wd == 'S':
        return 'South'
    elif wd == 'SSW':
        return 'South-Southwest'
    elif wd == 'SW':
        return 'Southwest'
    elif wd == 'WSW':
        return 'West-Southwest'
    elif wd == 'W':
        return 'West'
    elif wd == 'WNW':
        return 'West-Northwest'
    elif wd == 'NW':
        return 'Northwest'
    elif wd == 'NNW':
        return 'North-Northwest'
    else:
        return 'Unrecognized wind direction'


def translate_weather(weather):
    if weather == '1':
        return 'fas fa-cloud-sun'
    elif weather == '3':
        return 'fas fa-cloud'
    elif weather == '60':
        return 'fas fa-cloud-rain'
    elif weather == '61':
        return 'fas fa-cloud-showers-heavy'
    elif weather == '95':
        return 'fas fa-cloud-showers-heavy'  # Should be 'fas fa-thunderstorm' but it is a Pro Icon only


def create_webpage(filename):
    button_html = """          <li class="nav-item">
                <a class="nav-link active" href="javascript:change({id});">{date}</a>
              </li>"""
    hour_html = """          <div class="col-3 border">
                <div class="row justify-content-center">
                  <h3>{hour}:00</h3>
                </div>
                <div style="margin-top: 20px;" class="row justify-content-center">
                  <h3><i class="{weather_logo}"></i></h3>
                </div>
                <div style="margin-top: 20px;" class="row justify-content-center">
                  <h3>{humidity}%</h3>
                </div>
                <div class="row justify-content-center">
                  <h3>{temperature}\u00B0C</h3>
                </div>
                <div class="row justify-content-center">
                  <i class="fas fa-wind"></i>
                  <h4>{wind_speed}km/h</h4>
                </div>
                <div class="row justify-content-center">
                  <h5>{wind_direction}</h5>
                </div>
              </div>"""
    data = {}
    root = ET.parse(filename).getroot()
    for area in root.find("forecast").findall("area"):
        if not area.find("name").text == region_name:
            continue
        for parameter in area.findall("parameter"):
            param_id = parameter.get("id")
            for timerange in parameter.findall("timerange"):
                if timerange.get("type") == "hourly":
                    date = timerange.get("datetime")[:8]
                    hour = timerange.get("datetime")[8:10]
                    if param_id == 'ws':  # Take km/h value for wind speed
                        for values in timerange.findall("value"):
                            if values.get("unit") == 'KPH':
                                value = values.text
                                break
                    elif param_id == 'wd':  # Take wind direction value
                        for values in timerange.findall("value"):
                            if values.get("unit") == 'CARD':
                                value = values.text
                                break
                    else:
                        value = timerange.find("value").text
                    # Create nested dict if not exists yet
                    if date not in data:
                        data[date] = {}
                    if hour not in data[date]:
                        data[date][hour] = {}
                    data[date][hour][param_id] = value

    # print(data)
    # for day, day_data in data.items():
    #     print(f"{day[-2:]}/{day[-4:-2]}")
    #     for hour, hour_data in day_data.items():
    #         print(f"    Hour {hour}")
    #         for param_id, param_val in hour_data.items():
    #             print(f"        {param_id}: {param_val}")

    with open('template.html', 'r') as file:
        html = file.read()
        html = html.replace('{region_name}', region_name)
        button_list = []
        day_list = []
        for i, (day, day_data) in enumerate(data.items()):
            date = f"{day[-2:]}/{day[-4:-2]}"
            day_html = f"""        <div class="row" id="page{i + 1}">\n"""
            button_list.append(button_html.replace('{id}', str(i + 1)).replace('{date}', date))
            hour_list = []
            for hour_val, hour_data in day_data.items():
                hour = hour_html.replace("{hour}", hour_val).replace("{weather_logo}", translate_weather(hour_data['weather'])).replace("{humidity}", hour_data['hu']).replace("{temperature}", hour_data['t']).replace("{wind_speed}", str(round(float(hour_data['ws']), 2))).replace("{wind_direction}", translate_wd(hour_data['wd']))
                hour_list.append(hour)
            day_html += '\n'.join(hour_list) + '\n        </div>'
            day_list.append(day_html)
        html = html.replace('{button_list}', '\n'.join(button_list)).replace('{day_list}', '\n'.join(day_list))
        return html


if __name__ == '__main__':
    region_name = "Bandung"
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        title='Please select your XML file',
        filetypes=[('XML files', '*.xml'), ('All files', '*.*')],
    )
    html = create_webpage(filename)
    path = os.path.join(os.path.dirname(filename), 'weather.html')
    with open(path, 'w', encoding="utf-8") as html_file:
        html_file.write(html)
        print(f"HTML Weather Forecast saved at {path}!")
