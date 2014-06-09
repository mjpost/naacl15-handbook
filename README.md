Code for the ACL 2014 handbook.

ACL 2014 had five parallel sessions. This should be useful for any handbook 
where parallel sessions are listed one per page. 

Directories:

- `input/`: fixed inputs
   - `input/conferences.txt`: list of conferences

- `data/`: where the ACLPUB tarballs are downloaded and unpacked to

- `templates/`: template files used to seed the handbook

- `scripts/`: scripts used to generate the handbook sections from the ACLPUB
  proceedings.

- `content/`: handbook tex files

TODO

- Make sure biblatex-biber is installed

- Generate schedules and metadata for each workshop

- Fill in the tutorials manually, editing
  content/sunday/tutorials-001.tex and so on

- Generate CoNLL and CoNLL shared papers as separate auto-generated workshops, manually
  merge into content/

- handbook content is split into workshops (no abstracts) and main conference (abstracts)

- take schedule.tex files (formed treating order files as workshops)
  for papers, shortpapers, demos, and tacl and merge them under
  content, each of their days

- Generate the day overviews, munge them a bit, pull them in

 cat data/{papers,shortpapers,demos,tacl,srw}/proceedings/order | ./scripts/order2schedule_overview.py


- Mausam will cause you trouble. Grep for him. You want just the name,
  no {}s
  
- also special characters in abstracts (e.g., a real alpha, funny
  latex, chinese, etc)
  
- order files: should have just what they need, no full schedule in
  eahc. If session has papers from multiple (e.g., tacl, papers), make
  sure to have identical session header. use "papers" for full
  schedule of all events
