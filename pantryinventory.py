import json
import httplib2
import time
import datetime

baseUrl = "https://pantry-inventory.firebaseio.com/"

def findItem(allowNew):
    http = httplib2.Http('.cache')
    
    url = baseUrl + 'totals.json'
    resp_header, totalsJson = http.request(url, 'GET')
    totals = json.loads(totalsJson)

    validLow = 0 if allowNew else 1
    validHigh = len(totals)    

    valid = False
    while not valid:
        print
        print 'Select item:'
        if allowNew:
            print '0 - <New Item>'
        for x in range(0,len(totals)):
            print str(x + 1) + ' - ' + totals[x]['name']

        index = input('Select item number: ')
        if index != 0:
            if index >= validLow and index <= validHigh:
                name = totals[index - 1]['name']
                valid = True
            else:
                print 'Select a valid number'
                valid = False
        else:
            name = raw_input('Enter item name: ')
            valid = True
    qty = input('Enter quantity: ')
    return {"name":name, "qty": qty}


def showInventory():
    http = httplib2.Http('.cache')
    
    url = baseUrl + 'totals.json'
    resp_header, totalsJson = http.request(url, 'GET')
    totals = json.loads(totalsJson)
    printInventory(totals)


def printInventory(totals):
    print
    print 'Current Inventory:'
    for item in totals:
        print '   ' + item['name'] + ': ' + str(item['total'])


def adjustInventory(name, qty):
    http = httplib2.Http('.cache')
    total = qty
    
    # First - Increment total
    url = baseUrl + 'totals.json'
    resp_header, totalsJson = http.request(url, 'GET')
    totals = json.loads(totalsJson)
    # Find the item in the totals
    newItem = True
    for item in totals:
        if item['name'] == name:
            total = item['total'] + qty
            if total < 0:
                total = 0
                qty = item['total']
            item['total'] = total
            newItem = False
    if newItem:
        totals.append({'name': name, 'total': qty})
    printInventory(totals)
    # Update the database
    resp_header, resp_response = http.request(url, 'PUT', body=json.dumps(totals))
    
    # Second - Add to history
    url = baseUrl + 'history.json'
    resp_header, historyJson = http.request(url, 'GET')
    history = json.loads(historyJson)
    size = len(history)
    # Add a new entry
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    entry = {
        'name': name,
        'amount': qty,
        'total': total,
        'timestamp': st
        }
    url = baseUrl + 'history/' + str(size) + '.json'
    resp_header, resp_response = http.request(url, 'PUT', body=json.dumps(entry))


def addItem():
    item = findItem(True)
    name = item['name']
    qty = item['qty']

    adjustInventory(name, qty)


def removeItem():
    item = findItem(False)
    name = item['name']
    qty = item['qty']

    adjustInventory(name, -qty)

    

def menu():
    option = -1
    while option != 0:
        print '-- Main Menu --'
        print '1 - Add Item to inventory'
        print '2 - Remove Item from inventory'
        print '3 - Display current inventory'
        print '0 - Quit'
        option = input('Enter option: ')

        if option == 1:
            addItem()
        elif option == 2:
            removeItem()
        elif option == 3:
            showInventory()
        elif option == 0:
            print 'Bye'
        else:
            print 'Enter 0,1,2,3'
            input('Press <enter> to continue')

        print
        print


if __name__ == '__main__': #Calling from commandline
    menu()
