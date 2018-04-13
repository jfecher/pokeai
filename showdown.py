import os, sys
import subprocess
from threading import Thread
from queue import Queue, Empty

import pokemon

process = os.path.abspath("Pokemon-Showdown/pokemon-showdown")
showdown = subprocess.Popen([process, "simulate-battle"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

battle_format = "gen7randombattle"

def enqueue_output(out, queue):
    while True:
        for line in iter(out.readline, b''):
            queue.put(line.decode('utf-8'))

def send_msg(msg):
    global showdown
    showdown.stdin.write(b">")
    showdown.stdin.write(msg.encode('utf-8'))
    showdown.stdin.write(b"\n")
    showdown.stdin.flush()

def receive_msg():
    try:
        line = ''
        while True:
            line = line + str(showdown_queue.get_nowait())
    except Empty:
        return line

def print_backlog():
    msg = receive_msg()
    while msg:
        print(msg)
        msg = receive_msg()

# read updates from showdown asynchronously
showdown_queue = Queue()
showdown_thread = Thread(target=enqueue_output, args=(showdown.stdout, showdown_queue))
showdown_thread.daemon = True
showdown_thread.start()


send_msg('start {"formatid":"' + battle_format + '"}')
send_msg('player p1 {"name":"bot1"}')
send_msg('player p2 {"name":"bot2"}')

print_backlog()

p1 = ""
p2 = ""

while True:
    move = input("> ")
    send_msg(move)

    msg = receive_msg()
    if msg:
        p1, p2, updates = pokemon.parse_update(msg, p1, p2, battle_format)
        print(p1)
        print(p2)
        if updates:
            print(updates)

