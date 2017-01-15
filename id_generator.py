import os
import socket
import time
import string
import timeit
import unittest

__author__ = "Jeremy Farnault"

"""
Id generator
"""

# Constants

ALPHANUM = string.ascii_letters + string.digits
SIZE = 8


class UniqueId:
    def __init__(self):
        self.count = 0

    @staticmethod
    def convert(number):
        """
        Convert number an alphanum string
        :param number: a number to convert
        :return: a number converted in alphanum string
        :rtype: str
        """
        result = ""
        while number != 0:
            result = ALPHANUM[number % len(ALPHANUM)] + result
            number //= len(ALPHANUM)
        return result or "0"

    @staticmethod
    def complete_str(converted_string, size=SIZE):
        """
        Complete the string with "0" to fit the size and be sure that every id will have the same size
        :param converted_string: a converted string
        :param size: the wanted size for the converted string
        :return: the converted string with the wanted size
        :rtype: str
        """
        if len(converted_string) < size:
            return "0" * (size - len(converted_string)) + converted_string
        elif len(converted_string) == size:
            return converted_string
        else:
            return converted_string[len(converted_string) - size:]

    def get_process_hostname_id(self):
        """
        Generate a unique id with the system's hostname and the process id. Concatenate the first 4 converted characters
        of the process id with the converted sum of unicode values of the hostname.
        :return: 8 characters converted string
        :rtype: str
        """
        return self.complete_str(self.convert(os.getpid()), SIZE // 2)\
            + self.complete_str(self.convert(sum([ord(char) for char in socket.gethostname()])), SIZE // 2)

    def counter(self):
        """
        Counter to avoid collisions on the same node.
        :return: the counter value
        :rtype: int
        """
        if self.count >= 99999:
            self.count = 0
        self.count += 1
        return self.count

    def get_unique_id(self):
        """
        Create a unique id by concatenating :
        - "id"
        - the id obtained with the process id and the hostname
        - the converted current time (since epoch) in milliseconds
        - a counter to avoid collisions on the same node
        :return: the full generated id
        :rtype: str
        """
        return "id" + self.get_process_hostname_id() + \
               self.complete_str(self.convert(int(time.time() * 1000))) + \
               self.complete_str(self.convert(self.counter()))


class TestMethods(unittest.TestCase):
    def setUp(self):
        self.unique_id = UniqueId()

    def test_unique(self):
        """
        Test if all generated ids are unique
        """
        big_id_set = set()
        for i in range(100000):
            big_id_set.add(self.unique_id.get_unique_id())
        self.assertEqual(len(big_id_set), 100000)

    def test_time(self):
        """
        Test the time needed to generate an id 
        """
        time_per_id = timeit.timeit("uniq.get_unique_id()",
                                    setup="import id_generator; uniq = id_generator.UniqueId()",
                                    number=100000) / 100000
        # Check if at least 1000 ids are generated each seconds
        self.assertLess(time_per_id, 0.001)
        print("Generation of one id : {:.9f} second".format(time_per_id))


def generate_test_file(id_unique):
    """
    Create a text file with 50 million ids to check on the file size
    :param id_unique: object of the UniqueId type
    """
    test_file = open("50_million_unique_ids_file.txt", "w")
    for i in range(50000000):
        if i % 50000 == 0:
            print("{:.1f} %".format(i / 500000))
        test_file.write(id_unique.get_unique_id() + "\n")
    test_file.close()


def generate_batch(nbr_ids):
    """
    Generator used to create a batch of ids
    :param nbr_ids: the number of ids wanted in the batch
    """
    for i in range(nbr_ids):
        yield unique_id.get_unique_id()


if __name__ == '__main__':
    unique_id = UniqueId()
    choice = 0
    # Ask for the wanted mode
    print("Run tests, generate file with 50 million ids, generate batch of ids")
    while choice > 3 or choice < 1:
        choice = eval(input("[ 1 - Tests ; 2 - File ; 3 - Batch ]: "))
    print("")
    # Realize tests
    if choice == 1:
        print("Tests:")
        print("Test if all generated ids are unique")
        print("Test the time needed to generate an id ")
        uniq_id = unique_id.get_unique_id()
        print("Exemple of a generated ID : " + uniq_id)
        unittest.main()
    # Generate a massive file
    elif choice == 2:
        generate_test_file(unique_id)
    # Generate a batch of ids
    else:
        batch = generate_batch(eval(input("Number of ids: ")))
        file_name = input("File name: ")
        with open(file_name, 'w') as f:
            for x in batch:
                f.write(str(x) + "\n")
