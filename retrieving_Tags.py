import requests
from bs4 import BeautifulSoup #library that makes it easy to scrape information from web pages
with open('sample.html', mode='r') as f:
    html_doc=f.read() #the sample.html will cone as a string in html_doc

soup = BeautifulSoup(html_doc, 'html.parser')
print(soup.prettify())
#print(soup.title.string, type(soup.title.string))
#print(soup.div)#gives first div
#print(soup.find_all("div"))#finds all div
#print(soup.find_all("div")[1])#gives second div
for link in soup.find_all("a"):
    print(link.get("href"))
    print(link.get_text())

print(soup.select("div.italic")) #CSS SELECTOR
print(soup.select("div#italic")) #CSS SELECTOR
print(soup.span.get("class")) 
for child in soup.find(class_="container").children:#gives all children for a div
    print(child)
for parent in soup.find(class_="box").parents : #gives parent of the children whose class is box
    print(parent)  

#insert new tags in html file
ulTag=soup.new_tag("ul")

liTag=soup.new_tag("li")
liTag.string="Home"
ulTag.append(liTag)  

liTag=soup.new_tag("li")
liTag.string="About"
ulTag.append(liTag) 

soup.html.body.insert(0,ulTag)
with open("modified.html", "w") as f:
    f.write(str(soup))

def has_class_but_not_id(tag):
    return tag.has_attr("class") and not tag.has_attr("id")   

results=soup.find_all(has_class_but_not_id)
print(results)