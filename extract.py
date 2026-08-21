import zipfile
import xml.etree.ElementTree as ET
import sys
import io

def read_docx(path):
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = ET.XML(xml_content)

    paragraphs = []
    for paragraph in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [node.text
                 for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n'.join(paragraphs)

if __name__ == '__main__':
    content = read_docx(sys.argv[1])
    with open("prd_output.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("Done")
