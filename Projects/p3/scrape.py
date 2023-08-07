from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import pandas as pd
import os

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        file_nodes.clear()
        return self.dfs_visit(node)
        
    def dfs_visit(self, node):
        if node in self.visited:
            return
        self.visited.add(node)
        self.order.append(node)
        children = self.go(node)
        for child in children:
            self.dfs_visit(child)

    def bfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        file_nodes.clear()
        return self.bfs_visit(node)
    
    def bfs_visit(self, node):
        if node in self.visited:
            return
        self.visited.add(node)
        self.order.append(node)
        todo = [node]
        while len(todo)>0:
            curr = todo.pop(0)
            children = self.go(curr)
            for child in children:
                if not child in self.visited:
                    self.visited.add(child)
                    self.order.append(child)
                    todo.append(child)

class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def go(self, node):
        children = []
        for to_node, has_edge in self.df.loc[node].items():
            if has_edge == 1:
                children.append(to_node)
        return children

file_nodes = []
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
    
    def go(self, file): 
        with open(os.path.join('file_nodes', file), 'r') as f:
            lines = f.readlines()
            file_nodes.append(lines[0].strip())
            children = lines[1].strip().split(',')
        return children

    def message(self):
        msg = ''
        while len(file_nodes)>0:
            msg += msg.join(file_nodes.pop(0))
        return msg
        
        # msg = ''.join(map(str,file_nodes))
    
class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        self.driver = driver
        self.tbs = []
        super().__init__()

    def go(self, url):
        self.driver.get(url)
        links = self.driver.find_elements(by='tag name', value='a')
        self.tbs.append(pd.read_html(self.driver.page_source)[0])
        children = []
        for child in links:
            children.append(child.get_attribute("href"))
        return children
       
    def table(self):
        return pd.concat(self.tbs, ignore_index=True)

import time
import requests

def reveal_secrets(driver, url, travellog):
    driver.get(url)

    # Create password of clue sequence
    p = travellog.loc[:,"clue"].values.tolist()
    pwd = str()
    while len(p)>0:
        pwd += pwd.join(str(p.pop(0)))

    while True:
        time.sleep(4)
        try: 
            driver.find_element(value='password').send_keys(pwd)
            driver.find_element(value='attempt-button').click()
            driver.find_element(value='securityBtn').click()
        except NoSuchElementException:
            break
    
# copied/adapted from https://www.kite.com/python/answers/how-to-download-an-image-using-requests-in-python#:~:text=Use%20requests.,()%20to%20download%20an%20image&text=Use%20open(filename%2C%20mode),to%20write%20it%20to%20file%20.
    image_url = driver.find_element(value='image').get_attribute("src")
    r = requests.get(image_url)
    with open("Current_Location.jpg","wb") as f:
        f.write(r.content)
    
    return driver.find_element(value="location").text

# project: p3
# submitter: slu239
# partner: none
# hours: 10








     