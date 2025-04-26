from typing import Iterable, Sequence
from PIL import Image, ImageDraw, ImageFont

MAIN_MENU_CONTROLS = ['up', 'down', 'select']


class Page:
    def __init__(self, width: int, height: int, font: ImageFont, line_space: int) -> None:
        # tuple is (start_x, start_y, string)
        self.sentences: list[list[tuple[int, int, str]]] = []
        self.width = width
        self.height = height
        self.font = font
        self.line_height, descent = font.getmetrics()
        self.line_space = line_space if line_space >= descent * 2 else descent * 2
        self.max_lines = self.height // (self.line_height + self.line_space)
        if self.height % (self.line_height + self.line_space) >= (self.line_height + descent):
            self.max_lines += 1
        self.lines = ['']
        self.image = Image.new("1", (self.width, self.height), 255)
        self.image_drawn = False
        self.draw = ImageDraw.Draw(self.image)
        self.draw.font = self.font

    def draw_page(self) -> Image:
        self.image_drawn = True
        for i, line in enumerate(self.lines):
            self.draw.text((0, i * (self.line_height + self.line_space)), line)
        return self.image

    def draw_highlight_sentences(self, sentences: Sequence[int]) -> Image:
        if not self.image_drawn:
            self.draw_page()
        segments = []
        for sentence in sentences:
            segments.extend(self.sentences[sentence])
        return Display.highlight_text(self.image, segments, self.font)

    def add_sentence(self, sentence: str) -> str | None:
        # todo make it split words larger than width? or don't care - pretty sure will be unable to add at all currently
        start_x = self.draw.textlength(self.sentences[-1][-1][2] + ' ') if self.sentences else 0
        segment_start_word = 0
        words = sentence.split(' ')
        for i, word in enumerate(words):
            if not self.lines[-1]:
                new_line = word
            else:
                new_line = self.lines[-1] + ' ' + word
            line_length = self.draw.textlength(new_line)
            if line_length > self.width or i == len(words) - 1:
                added_words = ' '.join(words[segment_start_word:i if i < len(words) - 1 else i + 1])
                if added_words:
                    if segment_start_word == 0:
                        self.sentences.append([])
                    start_y = (len(self.lines) - 1) * (self.line_height + self.line_space)
                    self.sentences[-1].append((start_x, start_y, added_words))
            if line_length > self.width:
                if len(self.lines) == self.max_lines:
                    return ' '.join(words[i:])
                segment_start_word = i
                self.lines.append(word)
                start_x = 0
            else:
                self.lines[-1] = new_line

    @staticmethod
    def generate_pages(width: int, height: int, font: ImageFont, line_space: int, sentences: Iterable[str]
                       ) -> list['Page']:
        pages = [Page(width, height, font, line_space)]
        for sent in sentences:
            remainder = pages[-1].add_sentence(sent)
            while remainder:
                pages.append(Page(width, height, font, line_space))
                remainder = pages[-1].add_sentence(remainder)
        return pages


class Menu:
    pass


class Display:
    def __init__(self, width: int, height: int, font: ImageFont, button_height: int, line_space: int) -> None:
        self.width = width
        self.height = height
        self.font = font
        self.button_height = button_height
        self.line_space = line_space
        self.canvas = Image.new("1", (self.width, self.height))
        self.buttons = Image.new("1", (self.width, self.button_height))

    def paint_canvas(self) -> None:
        """
        Displays the canvas on the e-ink screen.
        """
        pass  # call function to draw canvas on ink screen

    def draw_screen(self, page: list[str]):
        screen = Image.new("1", (self.width, self.height - self.button_height))
        self.canvas.paste(screen, (0, 0))

    # def draw_button_labels(self, image: Image.Image, labels: list[str]):
    #     draw = ImageDraw.Draw(image)
    #     button_label_width = self.width / 4
    #     for i, label in enumerate(labels):
    #         draw.rectangle((button_label_width * i + H_SPACER, height - BUTTON_HEIGHT,
    #                         button_label_width * (i + 1) + H_SPACER, height - H_SPACER), outline=0)

    @staticmethod
    def highlight_text(image: Image, text: list[tuple[int, int, str]], font: ImageFont) -> Image:
        ascent, descent = font.getmetrics()
        box_height = ascent + descent
        highlighted_image = image.copy()
        draw = ImageDraw.Draw(highlighted_image)
        for item in text:
            draw.rectangle((item[0], item[1], item[0] + draw.textlength(item[2], font=font), item[1] + box_height),
                           fill=0)
            draw.text((item[0], item[1]), item[2], fill=255, font=font)
        return highlighted_image


# def scroll_menu(width, height, items, items_per_page, font):
#     images = []
#     pages = []
#     for i in range(0, len(items), items_per_page):
#         image = Image.new("1", (width, height), 255)
#         draw_button_labels(image, MAIN_MENU_CONTROLS, width, height)
#         draw = ImageDraw.Draw(image)
#         page_items = items[i:i + items_per_page]
#         box_height = (height - BUTTON_HEIGHT) / (items_per_page + 2)
#         first_item = ["Add_new"] if i == 0 else ["Previous page"]
#         last_item = ["Next page"] if i + items_per_page < len(items) else []
#         all_items = first_item + page_items + last_item
#         coordinates = []
#         for j, item in enumerate(all_items):
#             draw.rectangle((10, box_height * j, width - 10, box_height * (j + 1)), outline=0)
#             draw.text((15, box_height * j), item, font=font)
#             coordinates.append(((10, box_height * j, width - 10, box_height * (j + 1)), item))
#         pages.append(coordinates)
#         images.append(image)
#
#     return images, pages


sample_text = """It is now three years after the events of A New Hope. The Rebel Alliance has been forced to flee its base on Yavin 4 and establish a new one on the ice planet of Hoth.
An Imperial Star Destroyer, dispatched by the Sith Lord Darth Vader, continuing his quest for Luke Skywalker, launches thousands of probe droids across the galaxy, one of which lands on Hoth and begins its survey of the planet. Luke Skywalker, on patrol astride his tauntaun, discovers the probe, which he mistakes for a meteorite. After reporting to comrade Han Solo that he'll investigate the site, Luke is knocked unconscious by a deadly wampa.
When Luke fails to report in at Echo Base, Han Solo goes out on his tauntaun to search for him in an encroaching storm. Upon waking up, Luke finds himself hanging upside down in a cave; his eyes opening to the sight of a wampa eating his tauntaun. Using the power of the Force, Luke is able to pull his lightsaber out of the snow and to himself. After he ignites it, he cuts himself free and cuts off the attacking wampa's arm just in time, running out of the cave and escaping into the cold night of Hoth.
Luke tries to make his way to Echo Base on foot, but he finds himself lost in the blizzard and collapses in the snow. Suddenly, he sees the Force spirit of Obi-Wan Kenobi appear before him. Kenobi's spirit ghost instructs Luke to go to Dagobah to undergo training under Yoda, a Jedi Grand Master. After the spirit ghost disappears, Han arrives to find an almost unconscious Luke, who is mumbling indistinctly about Obi-Wan, Yoda, and Dagobah. Turning to his tauntaun, Han watches it collapse in the extreme cold. To keep Luke from freezing to death, Han uses Luke's lightsaber to cut open the dead tauntaun and places Luke in it. Han then sets about erecting a shelter for them both. They are forced to stay out during the night as the aircraft (snowspeeders) that the Rebels use for atmospheric flight had not yet been adapted for the extremely low temperatures of the planet and are therefore unable to mount a rescue operation.
The next morning, Rebel Pilots flying the snowspeeders set out from Echo Base to search for the missing men. Zev Senesca, one of the pilots in Rogue Group, makes contact with Han over comlink and the pair are rescued. When they are taken back to base, Luke is put in a bacta tank for healing under the care of medical droid, 2-1B.
Princess Leia Organa urges Han to stay with the Rebels. When Han assumes it is because she has feelings for him, Leia loses her temper and calls him a "stuck-up, half-witted, scruffy-looking nerf herder."
Meanwhile, the probe droid has spotted signs that indicate Hoth is occupied and sends a signal to the Imperial fleet, shortly before being shot at by Han Solo and Chewbacca and triggering its self-destruct mechanism. Aboard the Executor, Admiral Kendal Ozzel dismisses the information as evidence of smugglers, nothing more. However, Darth Vader knows better and orders the fleet to Hoth. Han warns General Rieekan that the Empire is probably aware of their location, and Rieekan orders the evacuation of Echo Base to begin.
Darth Vader and the Imperial forces set course for the Hoth system to set up the attack. The rebels load whatever equipment they can onto transports and plan a rear-guard action to secure their escape. Luke, now fully recovered from the Wampa attack and subsequent exposure, says farewell to Chewbacca and Solo, who have decided to leave the Alliance to resolve their debt to Jabba the Hutt. As the Imperial forces enter the Hoth system, General Rieekan orders full power to the energy shield that is protecting the base from orbital bombardment.
Aboard the Executor, General Maximilian Veers notifies Vader that Admiral Ozzel has emerged from lightspeed too close to Hoth. Ozzel intended to catch the Rebels unaware before they could set up their defenses. However, Vader realizes that the Rebels have been alerted to the fleet's arrival. Via video communication, Vader Force chokes Ozzel to death for his incompetence, then appoints Captain Firmus Piett the new Admiral on the spot. As Vader previously ordered, the Imperial ground forces, commanded by General Veers, land outside the Rebels' shield and march overland to destroy the power generator.
Princess Leia gives the Rebel fighters instructions on the evacuation to leave Hoth two to three ships at a time past the energy shield to a rendezvous point, which is beyond the outer rim. Rieekan lowers the shields to fire the Ion cannon at one of the Imperial Star Destroyers allowing the first transports to escape. The Rebel pilots assigned to hold off the Imperial ground assault depart the Hoth base for the oncoming battle against heavily equipped Imperial forces, who are armed with agile AT-STs (All Terrain Scout Transports) and monstrous AT-AT (All Terrain Armored Transport) walkers, led by General Veers."""

items = ["title1", "title2", "title3", "title4", "title5", "title6"]
# menu_images, menu_coordinates = scroll_menu(width, height, items, 4, font)

# for image in menu_images:
#     image.show()

# image = Image.new("1", (width, height), 255)
# pages = place_sentences(image, sentences, font, 0.0, 0.0, width, height)
# draw_page(image, pages[0])
# image = Image.new("1", (width, height), 255)
# draw_page(image, pages[1])
# image = Image.new("1", (width, height), 255)
#
# draw_page(image, pages[2])
#
# image = Image.new("1", (width, height), 255)
# for i in range(len(pages[0])):
#     highlight(image, pages[0], i)

if __name__ == '__main__':
    sentences = sample_text.replace("\n", "").split(".")
    if not sentences[-1]:
        sentences = sentences[:-1]
    sentences = [sentence.strip() + "." for sentence in sentences]
    d = Display(600, 400, ImageFont.load_default(), 0, 10)
    pages = Page.generate_pages(d.width, d.height, d.font, d.line_space, sentences)
    # for page in pages:
    #     page.draw_page().show()
    page = pages[0]
    print(page.sentences)
    page.draw_highlight_sentences([0]).show()
    page.draw_highlight_sentences([1]).show()
