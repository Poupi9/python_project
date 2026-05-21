from database import DatabaseManager
from models import Movie

SEED_MOVIES = [
    Movie(id=1, title="Inception", genre="Sci-Fi",
          synopsis="A thief who enters the dreams of others to steal secrets from their subconscious is offered a chance to have his criminal record erased if he can implant an idea into a target's mind.",
          year=2010, rating=8.8),
    Movie(id=2, title="The Dark Knight", genre="Action",
          synopsis="Batman raises the stakes in his war on crime. With the help of Lieutenant Gordon and District Attorney Harvey Dent, he sets out to dismantle the remaining criminal organizations that plague the city.",
          year=2008, rating=9.0),
    Movie(id=3, title="Interstellar", genre="Sci-Fi",
          synopsis="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival as Earth faces an environmental collapse.",
          year=2014, rating=8.6),
    Movie(id=4, title="The Shawshank Redemption", genre="Drama",
          synopsis="Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
          year=1994, rating=9.3),
    Movie(id=5, title="Parasite", genre="Drama",
          synopsis="Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
          year=2019, rating=8.5),
    Movie(id=6, title="The Grand Budapest Hotel", genre="Comedy",
          synopsis="The adventures of Gustave H, a legendary concierge at a famous European hotel, and Zero, the lobby boy who becomes his most trusted friend.",
          year=2014, rating=8.1),
    Movie(id=7, title="Get Out", genre="Thriller",
          synopsis="A young African-American visits his white girlfriend's parents for the weekend, where his simmering unease about their unusual behavior eventually reaches a breaking point.",
          year=2017, rating=7.7),
    Movie(id=8, title="Hereditary", genre="Horror",
          synopsis="After the family matriarch passes away, a grieving family is haunted by disturbing occurrences, eventually uncovering a terrifying truth about their ancestry.",
          year=2018, rating=7.3),
    Movie(id=9, title="Mad Max: Fury Road", genre="Action",
          synopsis="In a post-apocalyptic wasteland, Max teams up with a mysterious woman, Furiosa, to flee the tyrannical warlord Immortan Joe and his army across the desert.",
          year=2015, rating=8.1),
]


def seed(db: DatabaseManager) -> None:
    """Insert the initial movie catalogue into the database if it is empty."""
    if db.get_all_movies():
        return
    for movie in SEED_MOVIES:
        db.insert_movie(movie)
