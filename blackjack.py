"""
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>
"""
# Authored by Randy Graham Jr.
# randy@mitechmgmt.com
import os
from time import sleep
from random import shuffle
from msvcrt import getch
from platform import system

try:
    import colorama

    colorama.init()
    CARD_BACK_COLOR = colorama.Back.MAGENTA
    CARD_BACK_ACCENT = colorama.Fore.WHITE
    CARD_FRONT_COLOR = colorama.Back.WHITE
    CARD_RED_SUITE = colorama.Fore.RED
    CARD_BLACK_SUITE = colorama.Fore.BLACK
    RESET = colorama.Style.RESET_ALL
except ImportError:
    print("Colorama not found. Using Black+White mode.")
    sleep(1)
    CARD_BACK_COLOR = ""
    CARD_BACK_ACCENT = ""
    CARD_FRONT_COLOR = ""
    CARD_RED_SUITE = ""
    CARD_BLACK_SUITE = ""
    RESET = ""

CLEAR = lambda: os.system("cls" if system() == "Windows" else "clear")

suites = {
    "♥": CARD_RED_SUITE,
    "♦": CARD_RED_SUITE,
    "♠": CARD_BLACK_SUITE,
    "♣": CARD_BLACK_SUITE,
}

card_back_top = CARD_BACK_COLOR + CARD_BACK_ACCENT + "╔═╗" + RESET
card_back_middle = CARD_BACK_COLOR + CARD_BACK_ACCENT + "║@║" + RESET
card_back_bottom = CARD_BACK_COLOR + CARD_BACK_ACCENT + "╚═╝" + RESET

WIDTH = 119
HEIGH = 19


def printc(value):
    print(value.center(WIDTH))


def money(value):
    return f"${value:,.2f}"


def ynKeyInput():
    while True:
        char = getch()
        if char not in (b"y", b"n"):
            continue
        return char == b"y"


def inputc(prompt):
    centered = " " * ((WIDTH // 2) - (len(prompt) // 2))
    return input(centered + prompt)


class Card:
    def __init__(self, suite, value):
        self.suite = suite
        self.value = value

        if value == 1:
            self.glyph = "A"
            self.value = 11
        elif value == 11:
            self.glyph = "J"
            self.value = 10
        elif value == 12:
            self.glyph = "Q"
            self.value = 10
        elif value == 13:
            self.glyph = "K"
            self.value = 10
        else:
            self.glyph = str(self.value)

        if len(self.glyph) == 1:
            spacing = "  "
        else:
            spacing = " "

        self.topstring = (
            CARD_FRONT_COLOR + suites[self.suite] + self.glyph + spacing + RESET
        )
        self.middlestring = (
            CARD_FRONT_COLOR + suites[self.suite] + " " + self.suite + " " + RESET
        )
        self.bottomstring = (
            CARD_FRONT_COLOR + suites[self.suite] + spacing + self.glyph + RESET
        )

    def top(self, notvisible=False):
        if notvisible:
            return card_back_top
        return self.topstring

    def middle(self, notvisible=False):
        if notvisible:
            return card_back_middle
        return self.middlestring

    def bottom(self, notvisible=False):
        if notvisible:
            return card_back_bottom
        return self.bottomstring


class BlackJack:
    def __init__(self):
        self.player = []
        self.player_NV = []
        self.dealer = []
        self.dealer_NV = []
        self.wallet = 200
        self.insurance = False

        # Creates 6 decks of cards
        self.deck = [
            Card(suite, value) for suite in "♥♦♣♠" for value in range(1, 14)
        ] * 6
        shuffle(self.deck)
        self.discard = []
        self.start()

    def initial_deal(self):
        self.dealer.append(self.deck.pop())
        self.drawState()
        sleep(0.6)

        self.player.append(self.deck.pop())
        self.drawState()
        sleep(0.6)

        self.dealer.append(self.deck.pop())
        self.dealer_NV.append(1)
        self.drawState()
        sleep(0.6)

        self.player.append(self.deck.pop())
        self.drawState()
        sleep(0.6)

    def start(self, bet=25):
        # reset game
        self.dealer_NV = []
        self.player_NV = []
        self.insurance = False
        self.bet = bet
        self.wallet -= bet

        while len(self.player) > 0:
            self.discard.append(self.player.pop())

        while len(self.dealer) > 0:
            self.discard.append(self.dealer.pop())

        if len(self.deck) < 75:
            while len(self.discard) > 0:
                self.deck.append(self.discard.pop())
            shuffle(self.deck)

        for c in self.deck:
            if c.value == 1:
                c.value = 11

        # Deal the Cards
        self.initial_deal()

        # Check for Insurance Bet
        if self.dealer[0].value == 11:
            printc("Place insurance bet? (y/n)")
            if ynKeyInput():
                self.insurance = min(float(inputc("How much? ")), self.bet / 2)
                self.wallet -= self.insurance
                self.drawState()

        # Check for Dealer Natural
        if self.dealer_value() == 21:
            if self.insurance:
                printc("Dealer had a natural!")
                self.wallet += self.insurance * 2
                self.drawState()
            self.dealer_turn()

        if self.insurance:
            printc("Dealer didn't have a natural...")
            sleep(0.8)

        # Check for Player Natural
        if self.player_value() == 21:
            printc("Player Natural!")
            self.player_win()

        # Check for Double Down
        if self.player_value() in (9, 10, 11):
            printc("Would you like to double down? (y/n)")
            if ynKeyInput():
                self.wallet -= self.bet
                self.bet *= 2
                self.player.append(self.deck.pop())
                self.player_NV.append(len(self.player) - 1)
                self.dealer_turn()

        # Player Turn
        while self.player_value() < 21:
            printc("Hit? (y/n)")
            if ynKeyInput():
                self.player.append(self.deck.pop())
                self.drawState()
                sleep(0.25)
            else:
                break

        if self.player_value() > 21:
            printc("You Busted!")
            printc("You lost your bet...")
            inputc("Press Enter to Try Again!")
            self.start()

        # Dealer Turn
        self.dealer_turn()

    def dealer_turn(self):
        self.dealer_NV = []
        self.drawState()
        sleep(0.8)
        while self.dealer_value() < 17:
            self.dealer.append(self.deck.pop())
            self.drawState()
            sleep(0.8)

        if self.dealer_value() > 21:
            printc("Dealer Busted!")
            self.player_win()

        if len(self.player_NV) > 0:
            self.player_NV = []
        self.drawState()
        sleep(0.8)

        if self.player_value() > self.dealer_value():
            printc("Player is closer to 21 than dealer!")
            self.player_win()
        elif self.player_value() < self.dealer_value():
            printc("Dealer is closer to 21 than player...")
            printc("You lost your bet!")
            inputc("Press Enter to Play Again!")
            self.start()
        else:
            printc("Standoff!")
            self.wallet += self.bet
            inputc("Press Enter to Play Again!")
            self.start()

    def player_win(self):
        printc(f"You won {money(self.bet*2)}!")
        self.wallet += self.bet * 2
        inputc("Press Enter to Play Again!")
        self.start()

    def dealer_value(self):
        result = sum([c.value for c in self.dealer])
        if result > 21:
            for c in self.dealer:
                if c.value == 11:
                    c.value = 1
                    return self.dealer_value()
        return result

    def player_value(self):
        result = sum([c.value for c in self.player])
        if result > 21:
            for c in self.player:
                if c.value == 11:
                    c.value = 1
                    return self.player_value()
        return result

    def drawState(self):
        CLEAR()
        print(money(self.wallet).rjust(WIDTH))

        print("═" * WIDTH)

        if len(self.dealer_NV) == 0:
            printc(str(self.dealer_value()))
        else:
            print()

        tops = []
        middles = []
        bottoms = []
        for i, c in enumerate(self.dealer):
            tops.append(c.top(i in self.dealer_NV))
        for i, c in enumerate(self.dealer):
            middles.append(c.middle(i in self.dealer_NV))
        for i, c in enumerate(self.dealer):
            bottoms.append(c.bottom(i in self.dealer_NV))

        centered = (WIDTH // 2) - ((len(tops) // 2) + len(tops) - 1)

        print(" " * centered + " ".join(tops))
        print(" " * centered + " ".join(middles))
        print(" " * centered + " ".join(bottoms))

        print()
        printc(money(self.bet))
        print()

        tops = []
        middles = []
        bottoms = []

        for i, c in enumerate(self.player):
            tops.append(c.top(i in self.player_NV))
        for i, c in enumerate(self.player):
            middles.append(c.middle(i in self.player_NV))
        for i, c in enumerate(self.player):
            bottoms.append(c.bottom(i in self.player_NV))

        centered = (WIDTH // 2) - ((len(tops) // 2) + len(tops) - 1)

        print(" " * centered + " ".join(tops))
        print(" " * centered + " ".join(middles))
        print(" " * centered + " ".join(bottoms))
        if len(self.player_NV) == 0:
            printc(str(self.player_value()))
        else:
            print()
        print("═" * WIDTH)


BlackJack()
