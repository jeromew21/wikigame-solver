# WIKIGAMER

The wikigame is simply stated as finding the shortest path in the Wikipedia graph. In more concrete terms: finding the least number of hops from one page to another. Some variations are "fewest clicks", "fastest time" and "fewest clicks to Jesus" (or if you're feeling edgy, fewest to Hitler).

Some rules:

1. No using portals or help pages; stick to articles
2. Don't use country pages or disambiguation pages (though this is kind of a slippery slope and not really enforced)

## Part 1: Crawling

Use multiprocessing to speed things up a ton. Since web requests are slow and asynchronous, you can get a ridiculous speedup from doing a bunch at the same time. Python's multiprocessing module makes this fairly easy. It even has a way to use threads instead of spawning new processes, with the same API (!). This stopped my computer from getting nice and toasty.

There are only (?) five million or so English articles, so getting most all of them shouldn't be too lengthy of a task.

Data is saved in SQLite for stability.

## Part 2: Searching

naive BFS gives decent results. 

Using Djikstra's means having to assign edge weights. It turns out that assigning lower edge weights to more specific articles (ones later in the parent) actually gives a better result for some searches.

### Useful stuff

SQLite --- a great tool for storing lots of data locally. 

Multiprocessing --- doing this for scraping is a lifesaver, but on my unstable internet at home it can hang, likely due to inconsistent latency

namedtuple --- very useful for creating a quick semantic construct, but with much better performance than writing a class and instantiating objects (because it uses a tuple under the hood, while classes have a bunch of overhead)
