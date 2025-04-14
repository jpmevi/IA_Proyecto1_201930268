import random
class Seleccionador:
    def seleccionar(self, poblacion, k):
        torneo = random.sample(poblacion, k)
        return max(torneo, key=lambda i: i.aptitud)
