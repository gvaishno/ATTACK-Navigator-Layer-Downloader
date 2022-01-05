# Import Module
import os, requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

dir_path = os.path.dirname(os.path.realpath(__file__))

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("log-level=3")
chrome_options.add_argument("--disable-web-security")
chrome_options.w3c = True
prefs = {"download.default_directory" : dir_path+"\downloads"}
chrome_options.add_experimental_option("prefs",prefs)

# Open Chrome
driver = webdriver.Chrome(executable_path=dir_path+"\chromedriver.exe", options=chrome_options)

# Get all groups mentioned in the page.
def get_groups(driver):
    target_url = "https://attack.mitre.org/groups/"
    driver.get(target_url)
    
    # Find table by xpath
    table_id = driver.find_element_by_xpath("/html/body/div/div[3]/div[2]/div/div[2]/div/div/div/div/table")
    # Get first column
    first_column = table_id.find_elements_by_xpath(".//tbody/tr/td[1]")
    second_column = table_id.find_elements_by_xpath(".//tbody/tr/td[2]")
    groups_id = []
    groups_name = []
    for row in first_column:
        groups_id.append(row.text)
    for row in second_column:
        groups_name.append(row.text)

    # Zip two lists
    groups = list(zip(groups_id, groups_name))
    return groups


# Download the file from the navigator page.
def download_file(driver):
    groups = get_groups(driver)
    driver.get("https://attack.mitre.org/")
    primary_tab = driver.window_handles[0]

    print ("[*] Downloading the file...")
    for group in groups:
        group_id = group[0]
        group_name = group[1]

        navigator_url = "https://mitre-attack.github.io/attack-navigator//#layerURL="

        # Verify and build download link
        try:
            url = "https://attack.mitre.org/groups/"+group_id+"/"+group_id+"-enterprise-layer.json"
            response = requests.get(url)
            if response.status_code == 200:
                target_url = navigator_url+url
            else:
                # Change the url to mobile-layer.json
                url = "https://attack.mitre.org/groups/"+group_id+"/"+group_id+"-mobile-layer.json"
                response = requests.get(url)
                if response.status_code == 200:
                    target_url = navigator_url+url
        except:
            print ("[!] Error: "+group_name+" is not available.")
            continue

        driver.switch_to.window(primary_tab)
        print ("[*] Downloading the file for group: " + group_name)

        # Open the navigator page and download the file.
        driver.execute_script("window.open('"+target_url+"');")

        # Maintaining at least one tab open till the end.
        secondry_tab = driver.window_handles[1]
        driver.switch_to.window(secondry_tab)

        # Wait for the page to load
        driver.implicitly_wait(10)


        # Download the file by clicking the button.
        driver.find_element_by_xpath("/html/body/app-root/div/div/div/tabs/datatable/div[1]/ul/li[2]/div[3]/div/span").click()

        # Verify the file is downloaded.
        group_name = group_name.replace(" ", "_")
        if os.path.isfile(dir_path+"\downloads\\"+group_name+"_("+group_id+").json"):
            print("File downloaded: "+group_name+"_("+group_id+").json")

        # Close the secondary tab.
        driver.close()
    
        

# print(get_groups(driver))
download_file(driver)
print ("Total files: "+str(len(os.listdir(dir_path+"\downloads"))))
print ("[*] Done.")

# Close Chrome
driver.quit()
