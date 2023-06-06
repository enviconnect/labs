# enviConnect Labs

## Service provider

This website is provided by:

Andrew Clifton  
TGU enviConnect  
TTI – Technologie-Transfer-Initiative GmbH an der Universität Stuttgart (TTI GmbH)  
Nobelstrasse 15  
70569 Stuttgart  
Germany

Please mail [info@enviconnect.de](info@enviconnect.de)

# Notes to deployment at pythonanywhere

- Pythonanywhere has heavy limits on quota. This means that a virtual environment can take the disk requirements over quota. Consider deploying without a virtual environment, and then just doing `pip install -r requirements.txt`.
- Install extra fonts to allow the wordcloud to work. See https://help.pythonanywhere.com/pages/Fonts/ for details.
