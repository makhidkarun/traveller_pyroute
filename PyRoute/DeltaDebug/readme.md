Delta Debugging for PyRoute
===========================

What is delta debugging?
------------------------
Delta debugging is an approach to shrinking a failure-causing input by removing parts of that input whose presence is accidental - that part didn't cause the failure, it just happened to be in the neighbourhood.

In other words, the input has an essential core, alongside a mass of irrelevant dross.  Delta debugging aims to preserve that essential core, and remove as much of the dross as it can, while still causing the original problem.

Why should I care?
------------------
If you're reading this, you've likely run into some problem with PyRoute, and you'd prefer to see it fixed.

The more effort _you_ put into making your problem simple to understand and, more importantly, reproduce, the more likely it is to be fixed in the first place, fixed _correctly_, and _stay fixed_.

To help you simplify your problem, enter delta debugging, stage left.

Reducing the sheer size of your failure-causing input doesn't bog down the person fixing it with (quite as much) irrelevant stuff.

For example, one of PyRoute's major contributors, Alex Goodwin, has found digging through Dagudashaag's entirety (558 stars) in pursuit of a bug to be too difficult.  A shrunken 16-star Dagudashaag, on the other end, is no problem.

A reduced-size test case also helps identify (semi-)duplicate reported bugs, by making it more obvious those reports are different facets of the same underlying problem.

How is delta debugging being applied here, and what problem is it solving?
-----------------
PyRoute's version of delta debugging takes a list of input sectors, a definition of the problem, and by default, tries to reduce the size of the input by:

- Discarding irrelevant sectors completely
- Discarding irrelevant subsectors
- Discarding irrelevant star systems

This default setting works reasonably well - in the worked example below, starting with Zarushagar and a broken copy of Dagudashaag (approx 1050 stars in total), those default settings reduced the input to 1 sector file (Dagudashaag) with only 2 star systems in it.

There are three extra, currently-experimental, passes available:
- Discarding irrelevant allegiances (runs after sector discard)
- Discarding irrelevant _pairs_ (not merely adjacent pairs) of star systems (runs after single-system discard)
- Discarding irrelevant _portions_ (eg trade codes, high/low TL) of a given star system (runs after double-system discard)

You might need one or more of these experimental passes if your particular problem doesn't reduce well with the standard ones.

How do I run it?
----------------


What do I do with the result?
---------
