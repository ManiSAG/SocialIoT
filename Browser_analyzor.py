import pyshark
from nested_dict import nested_dict
import pymysql





# Open database connection
db = pymysql.connect("localhost","root","Vahid737","lan_hosts" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

nd = nested_dict(2, list)


input_pcap = '/root/captures/browser.bk.pcap'

cap = pyshark.FileCapture(input_pcap,display_filter="browser")


def run_complex_command(command,cursor):
    drp_command = "DROP PROCEDURE IF EXISTS select_or_insert;"
    cursor.execute(drp_command)
    print(command)
    cursor.execute(command)
    call_command = "call select_or_insert(); "
    cursor.execute(call_command)


def print_conversation_header(pkt):
    my_data = pkt['BROWSER']

    if str(pkt['BROWSER'].command) ==  '0x00000001': # Host Announcement
        server = my_data.server
        comment = my_data.comment
    elif str(pkt['BROWSER'].command) ==  '0x0000000c':
        server = my_data.mb_server
    elif str(pkt['BROWSER'].command) == '0x00000008': #bowser election Request
        server = my_data.server
    elif str(pkt['BROWSER'].command) == '0x00000002': #Request Announcement
        try:
            server = my_data.response_computer_name
        except AttributeError as e:
            pass
    elif str(pkt['BROWSER'].command) == '0x00000009': #Request Announcement
        pass

    try:
        nd[pkt.ip.addr]['server'] = server
        nd[pkt.ip.addr]['comment'] =comment
        # print(nd[pkt.ip.addr])
    except AttributeError as e:
        if str(e) == 'No attribute named ip':
            try:
                nd[pkt.eth.src]['server'] = server
                nd[pkt.eth.src]['comment'] = comment
                # print(str(nd[pkt.eth.src]) + "!!!!!!!!!!!!!!!!")
            except Exception as e:
                # print(e)
                return
        return
    except Exception as e:
        if 'referenced before assignment' not in str(e):
            # print(e)
            pass
        return


cap.apply_on_packets(print_conversation_header)

for key in nd:
    print(key + " : " + str(nd[key]['server'])  + " , " + str(nd[key]['comment']))


for ip_addr in nd:
    browser_comment = ''
    browser_server = nd[ip_addr]['server']
    if browser_comment == '00':
        browser_comment = ''
    if 'comment' in nd[ip_addr].keys():
        if nd[ip_addr]['comment'] not in  ['00'] and not isinstance(nd[ip_addr]['comment'], list):
            browser_comment = nd[ip_addr]['comment']

    if ":" in ip_addr:
        Mac_addr = ip_addr
        command = '''create procedure select_or_insert()\
            begin \
                IF EXISTS(SELECT * FROM resolution WHERE `MAC_addr` = "{}" ) THEN\
                    UPDATE `resolution` SET  `browser_server` = "{}", `browser_comment` = "{}" WHERE `MAC_addr` = "{}";\
                ELSE\
                    INSERT INTO `resolution`(`IP_addr`, `MAC_addr`, `browser_server`, `browser_comment`) VALUES ("","{}","{}","{}");\
                END IF;\
            END '''.format(Mac_addr, browser_server, browser_comment, Mac_addr, Mac_addr, browser_server, browser_comment)
    else:
        command = '''create procedure select_or_insert()\
                    begin \
                        IF EXISTS(SELECT * FROM resolution WHERE `IP_addr` = "{}" ) THEN\
                            UPDATE `resolution` SET  `browser_server` = "{}", `browser_comment` = "{}" WHERE `IP_addr` = "{}";\
                        ELSE\
                            INSERT INTO `resolution`( `IP_addr`, `browser_server`, `browser_comment`) VALUES ("{}","{}","{}");\
                        END IF;\
                    END '''.format(ip_addr, browser_server, browser_comment, ip_addr, ip_addr, browser_server, browser_comment)
    run_complex_command(command,cursor)

db.commit()
db.close()