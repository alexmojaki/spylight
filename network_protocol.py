import socket

def recv_end(the_socket):
    Max = 10000
    End = "\n\n"
    total_data=[]
    data=''
    i = 0
    while True:
        i += 1
        if i > Max:
            break
        try:
            data = the_socket.recv(8192)
            if End in data:
                total_data.append(data[:data.find(End)])
                break
            total_data.append(data)
            if len(total_data) > 1:
                #check if end_of_data was split
                last_pair=total_data[-2]+total_data[-1]
                if End in last_pair:
                    total_data[-2]=last_pair[:last_pair.find(End)]
                    total_data.pop()
                    break
        except socket.error, e:
            break
    return ''.join(total_data)

OBJECT_TXT = "d"
SHOOT_TXT = "sh"
TRAPPED_TXT = "t"
DEAD_TXT = "d"
LOST_TXT = "l"
ACTIVATE_TXT = "a"
RUN_TXT = "r"
BEEP_TXT = "b"
NOISE_TXT = "n"
CAPTURE_TXT = "c"
SPY_TXT = "s" # no new line there, first line of the msg
MERCERNARY_TXT = "m" # no new line there, first line of the msg
SPY_TYPE = 1
MERCENARY_TYPE = 2
MSG_END = "\n\n"

(OT_MINE, OT_MIRROR, OT_DETECTOR) = range(0, 3)