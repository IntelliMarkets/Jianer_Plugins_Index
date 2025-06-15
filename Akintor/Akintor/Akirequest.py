import cloudscraper
from bs4 import BeautifulSoup
import yaml
import os
class AkinatorError(Exception):
    pass

class Akinator():
    def __init__(self, theme: str = "characters", lang: str = "jp", child_mode: bool = False) -> None:
        global proxyurl
        global lang114514
        global proxyuse
        global proxyurltwo
        proxyuse = False
        try:
            with open(os.path.abspath("./plugins/Akintor/config.yaml"), 'r') as f:
                data = yaml.safe_load(f)
            proxyurl = data.get('proxyurl', None)
            proxyurltwo = proxyurl
            lang114514 = data.get('lang', 'jp')
            if proxyurl:
                proxyurl = f"{proxyurl}https://{lang114514}.akinator.com/"
                proxyuse = True
            else:
                proxyurl = f"https://{lang114514}.akinator.com/"
                proxyuse = False
        except FileNotFoundError:
            print(f"❌ 文件 config.yaml 不存在，使用默认值")
            proxyurl = "https://jp.akinator.com/"
            lang114514 = "jp"
            proxyuse = False
        except yaml.YAMLError:
            print("❌ YAML 文件格式错误，使用默认值")
            proxyurl = "https://jp.akinator.com/"
            lang114514 = "jp"
            proxyuse = False
        self.ENDPOINT = proxyurl
        self.name = None
        self.description = None
        self.photo = None
        self.answer_id = None
        self.akitude = None
        self.scraper = cloudscraper.create_scraper() # 创建 cloudscraper 实例

        if theme == "characters":
            sid = 1
        elif theme == "objects":
            sid = 2
        elif theme == "animals":
            sid = 14
        else:
            raise AkinatorError("the theme must be 'characters' / 'objects' / 'animals'")
        self.json = {
            "step": 0,
            "progression": 0.0,
            "sid": sid,
            "cm": child_mode,
            "answer": 0,
        }

    def start_game(self):
        self.name = None
        self.description = None
        self.photo = None
        self.answer_id = None
        if proxyuse == True:
            self.akitude = f"{proxyurltwo}https://en.akinator.com/assets/img/akitudes_670x1096/defi.png"
        else:
            self.akitude = f"https://en.akinator.com/assets/img/akitudes_670x1096/defi.png"
        # 使用 cloudscraper 发送 POST 请求
        game = self.scraper.post(f"{self.ENDPOINT}game", json={"sid": self.json["sid"], "cm": self.json["cm"]}).text
        soup = BeautifulSoup(game, "html.parser")
        askSoundlike = soup.find(id="askSoundlike")
        question_label = soup.find(id="question-label").get_text()
        session_id = askSoundlike.find(id="session").get("value")
        signature_id = askSoundlike.find(id="signature").get("value")
        self.json["session"] = session_id
        self.json["signature"] = signature_id
        self.step = 0
        self.progression = 0.0
        self.question = question_label
        return question_label

    def post_answer(self, answer: str):
        if answer == "y":
            self.json["answer"] = 0
        elif answer == "n":
            self.json["answer"] = 1
        elif answer == "idk":
            self.json["answer"] = 2
        elif answer == "p":
            self.json["answer"] = 3
        elif answer == "pn":
            self.json["answer"] = 4
        else:
            raise AkinatorError("the answer must be 'y' / 'n' / 'idk' / 'p' / 'pn'")
        try:
            # 使用 cloudscraper 发送 POST 请求
            progression = self.scraper.post(f"{self.ENDPOINT}answer", json=self.json)
            progression = progression.json()
            if progression["completion"] == "KO":
                raise AkinatorError("completion : KO")
            elif progression["completion"] == "SOUNDLIKE":
                raise AkinatorError("completion : SOUNDLIKE")
            try:
                self.json["step"] = int(progression["step"])
                self.json["progression"] = float(progression["progression"])
                self.step = int(progression["step"])
                self.progression = float(progression["progression"])
                self.question = progression["question"]
                self.question_id = progression["question_id"]
                if proxyuse == True:
                    self.akitude = f"{proxyurltwo}https://en.akinator.com/assets/img/akitudes_670x1096/defi.png"
                else:
                    self.akitude = f"https://en.akinator.com/assets/img/akitudes_670x1096/defi.png"
            except:
                self.name = progression["name_proposition"]
                self.description = progression["description_proposition"]
                self.photo = progression["photo"]
                self.answer_id = progression["id_proposition"]
                self.json["step_last_proposition"] = int(self.json["step"])
            return progression
        except Exception as e:
            raise AkinatorError(progression)

    def go_back(self):
        self.name = None
        self.description = None
        self.photo = None
        self.answer_id = None
        if self.json["step"] == 0:
            raise AkinatorError("it's first question")
        if "answer" in self.json:
            del self.json["answer"]
        try:
            # 使用 cloudscraper 发送 POST 请求
            goback = self.scraper.post(f"{self.ENDPOINT}cancel_answer", json=self.json)
            goback = goback.json()
            self.json["step"] = int(goback["step"])
            self.json["progression"] = float(goback["progression"])
            self.step = int(goback["step"])
            self.progression = float(goback["progression"])
            self.question = goback["question"]
            self.question_id = goback["question_id"]
            if proxyuse == True:
                self.akitude = f"{proxyurltwo}https://en.akinator.com/assets/img/akitudes_670x1096/{goback['akitude']}"
            else:
                self.akitude = f"https://en.akinator.com/assets/img/akitudes_670x1096/{goback['akitude']}"
            return goback
        except:
            raise AkinatorError(goback)

    def exclude(self):
        self.name = None
        self.description = None
        self.photo = None
        self.answer_id = None
        if "answer" in self.json:
            del self.json["answer"]
        try:
            # 使用 cloudscraper 发送 POST 请求
            exclude = self.scraper.post(f"{self.ENDPOINT}exclude", json=self.json)
            exclude = exclude.json()
            self.json["step"] = int(exclude["step"])
            self.json["progression"] = float(exclude["progression"])
            self.step = int(exclude["step"])
            self.progression = float(exclude["progression"])
            self.question = exclude["question"]
            self.question_id = exclude["question_id"]
            if proxyuse == True:
                self.akitude = f"{proxyurltwo}https://en.akinator.com/assets/img/akitudes_670x1096/{exclude['akitude']}"
            else:
                self.akitude = f"https://en.akinator.com/assets/img/akitudes_670x1096/{exclude['akitude']}"
            return exclude
        except:
            raise AkinatorError(exclude)