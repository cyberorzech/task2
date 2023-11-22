# Zad 1

Informacje wrażliwe zostały zidentyfikowane w end poincie /customers podczas dodawania informacji dot. nowego klienta
<img width="1249" alt="image" src="https://github.com/Mixeway-Academy/task2/assets/50600293/3a33c8e8-c6e0-44e8-9115-eb6d259abe05">

Widoczny jest pełen zestaw informacji o kliencie, w tym pesel, adres.

Zadanie zostało rozwiązane zgodnie ze specyfikacją, tj. dane wrażliwe są maskowane bez zmiany formatu logów. Wykonano to poprzez modyfikację zachowania wybranego rozwiązania do logowania (pakiet loguru dostępny przez pip) oraz stosowne do formatu logów zdefiniowanego w dunder metodzie repr wyszukiwanie wrażliwych informacji (dowód na screenie: appNo jest maskowane). 
<img width="559" alt="image" src="https://github.com/Mixeway-Academy/task2/assets/50600293/9974ebe6-b237-4804-a87b-d31618f7f074">

Metoda ta jest wg mnie trudna w stosowaniu i utrzymaniu. Po pierwsze nie jest przenośna pomiędzy rozwiązaniami do logowania. Po drugie wymaga czasożernego pisania regexów. Po trzecie wymaga zmian za każdym razem kiedy format danych ulegnie zmianom - kosztowne utrzymanie. Po czwarte mogą być zawodne - jest to w końcu rodzaj blacklistingu. Przydatne byłoby wykorzystanie obiektów Read-Once i logowanie po odczycie danych na potrzeby DB, natomiast nie znalazłem wsparcia dla takich obiektów w języku python.

Rozwiązanie drugie, które zaproponowałem dodatkowo, opiera się na utworzeniu klasy ConfidentialInfoFlusher, która opiera się o whitelisting dozwolonych dla loggerów argumentów (napisałem też wersję z blacklistingiem - dwie wykomentowane instrukcje) i poprawnym, bezpiecznym formowaniu reprezentacji klasy w __repr__. Do użycia wymagane jest jedynie dziedziczenie po klasie ConfidentialInfoFlusher (najlepiej na 1 miejscu zgodnie z MRO jeśli dziedziczenie jest wielobazowe) oraz nie przesłanianie metody __repr__ w klasie dziedziczącej.
Zalety:

- bezbolesna konfiguracja dozwolonych/zabronionych parametrów (bez regexów)
- wrażliwe dane nie trafiają do logów niezależnie od ich formatu i zmian w czasie
- rozwiązanie nie wyklucza maskowania z poziomu loggera 

Implementacja jest również w PR, ale dla czytelności wrzucam snippet:

```python
class ConfidentialInfoFlusher:
    def __repr__(self):
        # keys_blacklist = ["ip", "pesel", "street", "password"]
        keys_whitelist = ["name"]
        # flushed_info = {k: self.__dict__[k] for k in self.__dict__.keys() - {*keys_blacklist}}
        flushed_info = {k: self.__dict__[k] for k in self.__dict__.keys() if k in keys_whitelist}
        return str(flushed_info)


class Test(ConfidentialInfoFlusher):
    def __init__(self, name=str, pesel=str):
        self.name = name
        self.pesel = pesel
        print(str(self))
```

# Zad 2
Przeskanowano 6 commitów i znaleziono 4 wycieki danych, które zostały sprawdzone pod kątem prawdziwości. W żadnym z nich nie wystąpiły wartości dynamicznie podmieniane - były to klucze prywatne zapisane jako tekst.

<img width="969" alt="image" src="https://github.com/Mixeway-Academy/task2/assets/50600293/ba0806dd-c1fe-4f5e-928b-9b3162b02b58">

Remediacja: przede wszystkim korzystanie z KMS czy to cloudowego (w scenariuszu, w którym jakiś provider jest wykorzystany) czy dockerowego (jako że aplikacja jest skonteneryzowana). Sekrety powinny być dynamicznie podstawiane, najlepiej generowane per build. Jeżeli nie można tak zrobić, należy przechowywać sekrety zapisane na dysku lokalnym gospodarza środowiska (hosta). Aby to robić bezpiecznie, należy:

- zweryfikować uprawnienia do odczytywania/zapisywania pliku, w którym są trzymane sekrety
- upewnić się, że pliki są uwzględnione w .gitignore (nie pojawia się w systemie kontroli wersji)
- zaimplementować wykorzystanie zmiennych środowiskowych, aby wartości sekretów były dostępne dla oprogramowania
- zadbać o kopie zapasowe kluczy poza hostem

# Zad 3
Wykonano skan projektu Pythonowego zgodnie z instrukcją.

<img width="566" alt="image" src="https://github.com/Mixeway-Academy/task2/assets/50600293/7872371b-920d-46d2-a4ba-f9101a8be2ac">

Aby dowiedzieć się czegoś więcej o tej pośredniej podatności (wynikającej z zależności naszej zależności), należałoby skorzystać z jakiegoś innego oprogramowania (np. Snyk), natomiast w tym przypadku wykonałem ręcznie szybki research. Okazuje się, że aktualizacja paczki healpy do wersji załatanej (1.16.0) nastąpiła 3 października br.

<img width="544" alt="image" src="https://github.com/Mixeway-Academy/task2/assets/50600293/c05abf35-e3a9-4199-b2ae-5d10e6ff47f8">

Najbliższa tej dacie podatność dot. libcurl to https://nvd.nist.gov/vuln/detail/CVE-2023-38545 - utworzona 18 października dzięki zgłoszeniu na hackerone z 10 października. 

Tutaj analiza podatności:
https://snyk.io/blog/curl-high-severity-vulnerability-oct-2023/ 

Oprogramowanie samo w sobie nie korzysta z tej zależności - wisi ona jedynie w pliku requirements-task.txt, toteż wskazane będzie usunięcie jej z zależności projektu zamiast aktualizacji. Jeżeli natomiast wymagane byłoby jej pozostawienie, jedyna wersja niepodatna na czas skanowania to ta wskazana przez raport, tj. 1.16.0, toteż drugą rekomendacją byłoby zaktualizowanie tej paczki (zmiana wersji w pliku requirements-task.txt) oraz sprawdzenie wystąpienia konfliktów z innymi paczkami.


