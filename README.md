Start with the html output from markdown, eg: git

Then run that html output through process_html.py, making sure you've enumerated the stylesheets that should be attached to it.

Right now those stylesheets are hard coded.

In the best case, the output would appear somewhere parallel to the input.

For the NFL Blog, there is also a bunch of kruft at the bottom of the page that needs to be removed or replaced with something cleaner.

----

Add
`padding-top:3rem; padding-left:3rem;` to the <body> tag

```<body style="margin:10 auto auto 0.8rem; padding:0; -ms-text-size-adjust:100%; -webkit-text-size-adjust:100%; padding-top:3rem; padding-left:3rem; font-family:var(--font-family); color:var(--text-color); background-color:var(--background-color); max-width:50em" bgcolor="var(--background-color)">
```

And change the date line to:
```<p class="date" style='margin-top: 0em; margin-bottom:1em; line-height:1.25; font-family:"monospace"; font-style:normal; font-weight:400; font-size:1em'>```

(shrink the margin between the author line and date line)

I changed the bgcolor in styles to: 

```

        :root {
            --color-gray-20: #e0e0e0;
            --color-gray-50: #C0C0C0;
            --color-gray-90: #333;
            --background-color: #EEEEEB;
            --text-color: var(--color-gray-90);
            --text-color-link: #d911a4;
            --text-color-link-active: #555;
            --text-color-link-visited: #2d2d2d;
            --syntax-tab-size: 2
        }
```