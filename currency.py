

class Convertor:

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):
        if not self._initialized:
            self.rates_to_usd = {
                "USD": 1.0,
                "EUR": 1.09,
                "JPY": 0.0067,
                "GBP": 1.27,
                "CNY": 0.14,
                "CHF": 1.13,
                "CAD": 0.74
            }
            self._initialized = True


    def convert(self, amount, from_currency, to_currency):
        if from_currency not in self.rates_to_usd or to_currency not in self.rates_to_usd:
            raise ValueError("Unsupported currency for conversion.")
        amount_in_usd = float(amount) * self.rates_to_usd[from_currency]
        return round(amount_in_usd / self.rates_to_usd[to_currency], 2)




class Currency:

    def __init__(self, amount, denom="USD"):
        self.amount = float(amount)
        self.denomination = denom.upper()
        self.helper = Convertor()


    def __str__(self):
        # Implement this or __repr__() (or both)
        pass


    def __repr__(self):
        # Implement this or __str__() (or both)
        pass


    def getAmount(self):
        # This should "tell" whoever asked how much currency there is of the currently chosen denomination
        pass


    def __add__(self):
        # This function handles what happens if something else is "added" to the currency; it should take in at least one other parameter.
        # This function should return something to where it's called.
        #
        # if 'chips' is some variable containing the currency object:
        #     newChips = chips + 5   -->   newChips = chips.__add__(5)
        pass


    def __iadd__(self):
        # This function handles what happens if something else is "added in place" to the currency; it should take in at least one other 
        # parameter. This function should not return anything, but SHOULD update the currency object.
        #
        # if 'chips' is some variable containing the currency object:
        #     chips += 5   -->   chips.__iadd__(5)
        pass


    def __sub__(self):
        # This function handles what happens if something else is "subtracted" from the currency; it should take in at least one other parameter.
        # This function should return something to where it's called.
        #
        # if 'chips' is some variable containing the currency object:
        #     newChips = chips - 5   -->   newChips = chips.__sub__(5)
        pass


    def __isub__(self):
        # This function handles what happens if something else is "subtracted in place" to the currency; it should take in at least one other 
        # parameter. This function should not return anything, but SHOULD update the currency object.
        #
        # if 'chips' is some variable containing the currency object:
        #     chips -= 5   -->   chips.__isub__(5)
        pass


    def __mul__(self):
        # This function handles what happens if the currency object is "multiplied" by something, whatever that means to you; it should take in 
        # at least one other parameter. This function should return something to where it's called.
        #
        # if 'chips' is some variable containing the currency object:
        #     newChips = chips * 5   -->   newChips = chips.__mul__(5)
        pass


    def __imul__(self):
        # This function handles what happens if the currency object is "multiplied" by something "in place", whatever that means to you; it 
        # should take in at least one other parameter. This function should return something to where it's called.
        #
        # if 'chips' is some variable containing the currency object:
        #     newChips *= 5   -->   newChips = chips.__imul__(5)
        pass


    def __truediv__(self):
        # This function handles what happens if the currency object is "divided" by something, whatever that means to you; it should take in 
        # at least one other parameter. This function should return something to where it's called.
        #
        # if 'chips' is some variable containing the currency object:
        #     newChips = chips / 5   -->   newChips = chips.__truediv__(5)
        pass


    def __itruediv__(self):
        # This function handles what happens if the currency object is "divided" by something "in place", whatever that means to you; it 
        # should take in at least one other parameter. This function should return something to where it's called.
        #
        # if 'chips' is some variable containing the currency object:
        #     newChips /= 5   -->   newChips = chips.__itreudiv__(5)
        pass


    def __floordiv__(self):
        # This function handles what happens if the currency object is "divided" by something using floor division, whatever that means to you;
        # Traditional floor division returns the nearest integer, rounded down, after performing division. This function should take in 
        # at least one other parameter and should return something to where it's called.
        #
        # if 'chips' is some variable containing the currency object:
        #     newChips = chips // 5   -->   newChips = chips.__floordiv__(5)
        pass


    def __round__(self, ndigits=0):
        # This function handles what happens if the currency object is rounded to some given decimal value, given as ndigits). This function should
        # update the currency object without returning something new to where it was called.
        pass


    def __eq__(self, other):
        # Remember that this function handles what it means to compare something against a currency object to see if the two are the same,
        # whatever 'the same' means to you.
        #
        # if 'chips' is some variable containing the currency object and 'otherChips' is some other object:
        #     chips == otherChips  -->  chips.__eq__(otherChips)
        pass


    def __lt__(self, other):
        # This function handles what it means to see if something else is "less than" our currency object, whatever that means to you.
        #
        # if 'chips' is some variable containing the currency object and 'otherChips' is some other object:
        #     chips < otherChips  -->  chips.__lt__(otherChips)
        pass


    def __gt__(self, other):
        # This function handles what it means to see if something else is "greater than" our currency object, whatever that means to you.
        #
        # if 'chips' is some variable containing the currency object and 'otherChips' is some other object:
        #     chips > otherChips  -->  chips.__gt__(otherChips)
        pass


    def __le__(self, other):
        # This function handles what it means to see if something else is "less than or equal to" our currency object, whatever that means to 
        # you.
        #
        # if 'chips' is some variable containing the currency object and 'otherChips' is some other object:
        #     chips <= otherChips  -->  chips.__le__(otherChips)
        pass


    def __ge__(self, other):
        # This function handles what it means to see if something else is "greater than or equal to" our currency object, whatever that means to 
        # you.
        #
        # if 'chips' is some variable containing the currency object and 'otherChips' is some other object:
        #     chips >= otherChips  -->  chips.__ge__(otherChips)
        pass


    def set_amount(self, amt):
        self.amount = float(amt)


    def convert(self, new_denom):
        newDenom = new_denom.upper()
        self.amount = self.helper.convert(self.amount, self.denomination, newDenom)
        self.denomination = newDenom

