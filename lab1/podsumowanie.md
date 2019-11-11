# Podsumowanie 

*det1* wyznacznik 3x3
*det2* wyznacznik 2x2

## Epsilon = 0
Gdy epsilon jest równy zeru między wyznacznikami nie ma więszej różnicy, jednak zauważyć można, że wyniki nie są identyczne.

## Epsilon = 10 ** -14
Przy małym epsilon wyznacznik det1 prawidłowo sklasyfikował wszystkie punky leżące na prostej, podczas gdy det2 poprawnie sklasyfikował około 60%.
Korzystając z tej obserwacji możemy zauważyć również że det2 prawdopodobnie źle sklasyfikował kilka punktów ze zbioru 2 jako leżące na prostej mimo, że na niej nie leżą.

## Wnioski
Wyznacznik *det1* jest znacznie precyzyjniejszy jeśli chodzi o sprawdzanie czy punkty leżą na prostej.
Zaletą *det2* jest mniejsza liczba instrukcji potrzebna do jego policzenia a szczególnie mniejsza liczba instrukcji mnożenia przez co jest on szybszy do wyliczenia.