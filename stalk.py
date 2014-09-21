#!/usr/bin/env python

import praw, sys
from pymarkovchain import MarkovChain
from random import shuffle

from models import Node

def main(username):
    r = praw.Reddit(user_agent='trollolol v0.1')
    r.config.decode_html_entities = True

    m = MarkovChain('markov-data/%s.chain' % username)

    last_comment = None
    try:
        last_comment = Node.objects(username=username).order_by('-created').first()
        if last_comment:
            print("Checking for new messages.")
            comments = r.get_redditor(username).get_comments(limit=500, params={'after': last_comment.node_id})
        else:
            raise
    except:
        print("No messages fetched yet, doing inital import")
        comments = r.get_redditor(username).get_comments(limit=500)

    for comment in comments:
        try:
            node = Node.objects.get(node_id=comment.name)
        except:
            node = Node(node_id = comment.name, parent_id=comment.parent_id, body=comment.body, created=comment.created, username=username)
            node.save()

    first_comment = Node.objects(username=username).order_by('+created').first()
    if first_comment:
        print("Checking for messages before %s." % first_comment.node_id)
        comments = r.get_redditor(username).get_comments(limit=500, params={'before': first_comment.node_id})

        for comment in comments:
            try:
                node = Node.objects.get(node_id=comment.name)
            except:
                node = Node(node_id = comment.name, parent_id=comment.parent_id, body=comment.body, created=comment.created, username=username)
                node.save()

    comments = Node.objects(username=username).all()

    corpus = []
    for comment in comments:
        corpus.append(comment.body)


    shuffle(corpus)
    if len(corpus) > 0:
        print("We have %i messages to work with. Building new markov corpus now." % len(corpus))
        m.generateDatabase(" ".join(corpus))

        print("Looking for acceptable output for first round of transforms.")
        output = []
        tries = 0 
        while len(output) < 10:
            tries = tries + 1
            result = m.generateString()
            if tries < 100:
                if len(result.split(" ")) >= 10:
                    sys.stdout.write("x")
                    output.append(result)
                else:
                    sys.stdout.write(".")


        print("")

        response = ""
        for result in output:
            response = response + " " + result

        print response
    else:
        print("No comments found.")

if __name__ == '__main__':
    try:
        username = sys.argv[1]
    except IndexError:
        print("\nYou must provide a username\nUsage: %s [username]\n" % sys.argv[0])
        quit()
    main(username=username)

