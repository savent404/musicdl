#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import json
from musicdl.musicdl import musicdl as mdl
from prettytable import PrettyTable

def get_config(logfile, proxies, save, count):
    config = {
        'logfilepath': logfile,
        'proxies': json.loads(proxies),
        'savedir': save,
        'search_size_per_source': int(count),
    }
    return config

def get_sources(targets):
    target_srcs = [
        'kugou', 'kuwo', 'qqmusic', 'qianqian', 'fivesing',
        'netease', 'migu', 'joox', 'yiting',
    ] if targets is None else [src.strip() for src in targets.split(',')]
    return target_srcs

def internal_score(item, algorithm):
    score = 0
    if item.get('singers') and len(item['singers']) > 0:
        score += 1
    if item.get('album') and len(item['album']) > 0:
        score += 1
    if item.get('has_lyric') and item['has_lyric'] == 'Y':
        score += 1
    if item.get('ext') and item['ext'] == 'flac':
        score += 5
    return score

@click.group()
def cli():
    pass

@click.command()
@click.argument('keyword')
@click.option('-l', '--logfile', default='musicdl.log', help='log file path')
@click.option('-p', '--proxies', default='{}', help='proxies')
@click.option('-s', '--save', default='music', help='save dir')
@click.option('-t', '--targets', default=None, help='targets')
@click.option('-c', '--count', default='5', help='count')
@click.option('-j', '--out_json', is_flag=True, help='output json')
@click.option('-a', '--algorithm', default='default', help='algorithm for sorting the results')
def search(keyword, logfile, proxies, save, targets, count, out_json, algorithm):
    config = get_config(logfile, proxies, save, count)
    sources = get_sources(targets)

    client = mdl(config=config)
    results = client.search(keyword, sources)
    flat_results = []

    for key, values in results.items():
        flat_results += values

    # pre-process the attributes
    for item in flat_results:
        item['has_lyric'] = 'Y' if item.get('lyric') and (len(item['lyric']) > 50) else '-'
        item['score'] = internal_score(item, algorithm)
    
    # ordered by attr 'score'
    flat_results = sorted(flat_results, key=lambda x: x['score'], reverse=True)

    if out_json:
        # serialize the results as json string
        results = json.dumps(flat_results, indent=4, ensure_ascii=False)
        print(results)
        return
    else:
        # print the results in a table
        keys = ['songid', 'singers', 'songname', 'album', 'filesize', 'duration', 'has_lyric', 'ext', 'source', 'download_url']
        readable_title = ['id', 'singer', 'name', 'album', 'size', 'duration', 'has lyric', 'format', 'source', 'url']
        tab = PrettyTable(readable_title)
        for item in flat_results:
            tmp = []
            for key in keys:
                tmp.append(item.get(key, '-'))
            tab.add_row(tmp)
        print(tab)


cli.add_command(search)

if __name__ == '__main__':
    cli()