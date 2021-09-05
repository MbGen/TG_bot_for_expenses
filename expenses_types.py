from pydantic import BaseModel
from os import path, curdir

import xml.etree.ElementTree as ET

current_directory = path.abspath(curdir)
path_to_xml = f"{current_directory}\\expenses.xml"


class Expenses(BaseModel):
    amount: float

    def create_xml(self) -> None:
        root = ET.Element("Expenses")
        tree = ET.ElementTree(root)
        with open(path_to_xml, "wb") as _:
            tree.write(_)

    def add_data_to_xml(self) -> None:
        tree = ET.ElementTree(file=path_to_xml)
        root = tree.getroot()

        expense = ET.Element(repr(self))
        expense.set("amount", str(self.amount))

        root.append(expense)
        
        with open(path_to_xml, "wb") as file:
            tree.write(file, xml_declaration=True)

    def save_expenses(self) -> None:
        if not path.exists(path_to_xml):
            self.create_xml()
            self.add_data_to_xml()
        else:
            self.add_data_to_xml()

    @staticmethod
    def get_expenses() -> dict[str, float]:
        tree = ET.ElementTree(file=path_to_xml)
        root = tree.getroot()

        expenses = {
            "ProductExpenses": 0,
            "TransportExpenses": 0,
            "TechnicExpenses": 0,
            "InternetExpenses": 0
        }

        for _, expense_type in enumerate(expenses):
            for _, node in enumerate(root.findall(expense_type)):
                expenses[node.tag] += float(node.attrib["amount"])

        return expenses

    def __repr__(self) -> repr:
        return self.__class__.__name__


class TransportExpenses(Expenses):
    pass


class ProductExpenses(Expenses):
    pass


class TechnicExpenses(Expenses):
    pass


class InternetExpenses(Expenses):
    pass


class OtherExpenses(Expenses):
    pass
