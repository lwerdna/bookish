#!/usr/bin/env python

import re
import sys

debug = False

def getHaysTranslation():
	global debug
	chapFiles = []
	for d in range(12):
		chapFiles.append('./source/meds_hays%02d.html' % (d+1))

	# state variables as we process lines	
	result = []
	book = []
	verse = ''
	for [i,fpath] in enumerate(chapFiles):
		book = []

		bookNum = i+1;
		if debug: print '<!-- ------------------- -->'
		if debug: print '<!-- switched to book %d -->' % bookNum
		if debug: print '<!-- ------------------- -->'
	
		fp = open(fpath)
		lines = fp.readlines()
		fp.close()
		lines = map(lambda x: x.rstrip(), lines)

		verse = []
		verseNum = 0;
	
		for line in lines:
			# skip whitespace lines
			if re.match('^\s*$', line):
				continue

			# em dash
			line = re.sub('\xe2\x80\x94', ' &mdash; ', line)
			line = re.sub('\xe2\x80\x99', "'", line)
			line = re.sub('\xe2\x80\x9c', '"', line)
			line = re.sub('\xe2\x80\x9d', '"', line)

			m = re.match(r'^.*<span class="calibre4"> (.*)</span>.*$', line)
			if m:
				# switch verses
				m2 = re.match(r'^.*<span class="calibre4"> \s*(\d+)\..*$', line)
				if m2:
					verseNumNew = int(m2.group(1))
					if verseNumNew != verseNum + 1:
						raise Exception("bad verse # on line: %s", line)

					if verse:
						book.append('<br>'.join(verse))
					verse = []

					verseNum = verseNumNew
					if debug: print "<!-- switched to verse %d -->" % verseNum
	
				# skip the stuff before a verse
				if verseNum <= 0:
					continue;
	
				#
				verse.append(m.group(1))
				if debug: print m.group(1)

		# remaining verse?
		if verse:
			book.append('<br>'.join(verse))
			verse = []
	
		# add book to result
		result.append(book)

	# done!
	return result

def getLongTranslation():
	global debug

	fp = open('./source/meditations.mb.txt')
	lines = fp.readlines()
	fp.close()
	lines = map(lambda x: x.rstrip(), lines)

	# state variables as we process lines	
	result = []
	book = []
	bookNum = 0
	verse = []
	verseNum = 0

	i = 0;
	while(i < len(lines)):
		if re.match(r'^-------.*$', lines[i]) and \
			re.match(r'^\s*$', lines[i+1]) and \
			re.match(r'^BOOK .*$', lines[i+2]):

			if(book):
				result.append(book)
			book = []

			bookNum += 1
			if debug: print '<!-- ------------------- -->'
			if debug: print '<!-- switched to book %d (%s) -->' % (bookNum, lines[i+2])
			if debug: print '<!-- ------------------- -->'

			verseNum = 1
			i += 4 

		if bookNum <= 0:
			i += 1
			continue

		if re.match(r'^THE END.*$', lines[i]):
			result.append(book)
			break;

		# consume non-blank lines as a verse
		if re.match(r'^\s*$', lines[i]):
			print 'line[%d]: %s' % (i-2, lines[i-2])
			print 'line[%d]: %s' % (i-1, lines[i-1])
			print 'line[%d]: %s' % (i, lines[i])
			print 'line[%d]: %s' % (i+1, lines[i+1])
			print 'line[%d]: %s' % (i+2, lines[i+2])
			raise Exception("unexpected whitespace at line %d: -%s-" % (i, lines[i]))

		verse = ['%d.' % verseNum]
		while 1:
			verse.append(lines[i])
			i += 1
			if re.match(R'^\s*$', lines[i]):
				i += 1
				break;
		book.append(' '.join(verse))
		verseNum += 1
		if debug: print "<!-- switched to verse %d -->" % verseNum

	# done!
	return result

if __name__ == '__main__':
	if sys.argv[1:]:
		debug = True

		if sys.argv[1] == 'long':
			print "testing the Long translation"
			result = getLongTranslation()
			print "George Long: %d books read" % len(result)
			for (i,book) in enumerate(result):
				print "book %d has %d verses" % (i+1, len(book))
		if sys.argv[1] == 'hays':
			print "testing the Hays translation"
			result = getHaysTranslation()
			print "Gregory Hays: %d books read" % len(result)
			for (i,book) in enumerate(result):
				print "book %d has %d verses" % (i+1, len(book))

		sys.exit(0)

	result1 = getLongTranslation()
	result2 = getHaysTranslation()

	assert(len(result1) == len(result2))

	print '[TOC]\n'

	for i in range(12):
		print '# Book %d' % (i+1)

		print '|Long | Hays|'
		print '|---- | ----|'

		# pad verses to max size
		m = max(len(result1[i]), len(result2[i]))
		result1[i] += ['']*(m - len(result1[i]))
		result2[i] += ['']*(m - len(result2[i]))

		for j in range(m):
			#print "len(result1[%d])=%d len(result2[%d])=%d m=%d j=%d" % \
			#	(i, len(result1[i]), i, len(result2[i]), m, j)
			print '|%s|%s|' % (result1[i][j], result2[i][j])

