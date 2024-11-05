from DiscordLevelingCard import RankCard, Settings, Sandbox
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from typing import Optional, Union
from io import BytesIO
from DiscordLevelingCard import RankCard, Settings, Sandbox

class dis_card(RankCard):
    def __init__(self, settings: Settings, avatar: str,
                  level:int, level_name:str, username:str,
                    current_exp:int, max_exp:int, voice_time: int,
                      rank:Optional[int] = None)-> None:
        
        super().__init__(settings, avatar, level, username, current_exp, max_exp, rank)
        self.level_name = level_name
        hour = voice_time//(60*60)
        minutes = int((voice_time%3600)//60)
        self.voice_time = f'{hour}ч {minutes}м' if hour!=0 else f'{minutes}м'

    async def card_gh(self, resize: int = 100)-> Union[None, bytes]:
        path = str(Path(__file__).parent)
        if isinstance(self.avatar, str):
            if self.avatar.startswith("http"):
                self.avatar = await RankCard._image(self.avatar)
        elif isinstance(self.avatar, Image.Image):
            pass
        else:
            raise TypeError(f"avatar must be a url, not {type(self.avatar)}") 

        background = self.background.resize((1000, 400))

        top = Image.open("shapka.jpg").resize((1000,50))

        background.paste(top,(0,0))
        avatar = self.avatar.resize((260, 260))
        avatar_with_border = ImageOps.expand(avatar,border=8,fill='black')

        new = Image.new("RGBA", avatar_with_border.size, (0, 0, 0))

        new.paste(avatar_with_border, (0,0))
        
        background.paste(new, (20,70))
        myFont = ImageFont.truetype(path + "/assets/newfont.ttf",42)
        small_Font = ImageFont.truetype(path + "/assets/newfont.ttf",28)
        big_Font = ImageFont.truetype(path + "/assets/newfont.ttf",46)

        draw = ImageDraw.Draw(background)
        top_text = self.level_name
        w = draw.textlength(top_text, font=big_Font)
        draw.text((500-w/2,0), top_text,font=big_Font, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        draw.text((330,60), 'ИМЯ',font=small_Font, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        draw.text((330,85), self.username,font=myFont, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        draw.text((330,150), 'РАНГ',font=small_Font, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        draw.text((330,175), str(self.rank),font=myFont, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        draw.text((330,240), 'УРОВЕНЬ',font=small_Font, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        draw.text((330,265), self._convert_number(self.level),font=myFont, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        exp = f'{self._convert_number(self.current_exp)}/{self._convert_number(self.max_exp)}'
        draw.text((570,400-50), exp,font=myFont, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        
        
        text_len = draw.textlength(self.voice_time, font=big_Font)
        draw.text((900-text_len,85), self.voice_time,font=big_Font, fill=self.text_color,stroke_width=1,stroke_fill=(0, 0, 0))
        head = Image.open("assets/headphones.png")
        head = head.resize((60,60))

        w = draw.textlength(exp, font=myFont)
        bar_exp = (self.current_exp/self.max_exp)*619
        if bar_exp <= 50:
            bar_exp = 50  
        im = Image.new("RGBA", (620, 30))
        draw = ImageDraw.Draw(im, "RGBA")
        draw.rectangle((0, 5, 619, 25), fill=(0,0,0,255))
        if self.current_exp != 0:
            draw.rectangle((0, 5, bar_exp, 25), fill=self.bar_color, outline='black', width=3)
            draw.circle((bar_exp,15),fill='white',outline='black', radius=15,width=3)
        background.paste(im, (330, 320), im.convert("RGBA"))

        print(text_len)
        background.paste(head,(830-int(text_len), 80), head.convert("RGBA"))
        image = BytesIO()
        if resize != 100:
            background = background.resize((int(background.size[0]*(resize/100)), int(background.size[1]*(resize/100))))
        background.save(image, 'PNG')
        image.seek(0)
        return image