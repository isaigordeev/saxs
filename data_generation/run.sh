source .venv/bin/activate

python generation.py -p "cubic" --mp "Pn3m"
python processing.py
python main.py -p "cubic" --mp "Pn3m"