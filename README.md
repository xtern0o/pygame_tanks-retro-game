# tanks retro game
###### Игра представляет собой простой 2D-платформер с видом сверху и интуитивно-понятным управлением.
## Режимы:
`PVE` (прохождение и создание уровней, сражение с искусственным интеллектом) и `PVP` (сражение между двумя игроками на одном компьютере)
## Техника
На данный момент предполагается реализовать 2 основных класса техники: `классический танк` (возможно создание подклассов легкого, среднего, тяжелого) и `артиллерии`, стрельба которой будет производиться по клику мыши в определенную область карты.
## Остальное
`бустеры`, которые временно улучшают различные характеристики, `мины`, `разрушаемые стены`, `кусты`, которые дают невидимость на время нахождения в них.

# ТЗ
 - [x] Реализовать класс `ClassicTank` и `ClassicPlayer` с функцией управления игроком
 - [x] Реализовать класс `Bullet`
 - [ ] Реализовать класс `Artillery` + `ArtilleryPlayer`
 - [x] Реализовать класс `Map` и функцию `genereate_level()`
 - [x] Реализовать класс `ClassicTankBot`, являющийся аналогом классического танка с готовым искусственным интеллектом (алгоритмом)
 - [x] Реализовать классы бустеров `SpeedBooster`, `DamageBooster`, `ArmorBooster`, `HealthBooster`
 - [x] Реализовать механику разрушаемых и(или) неразрушаемых стен, кустов
 - [ ] Разработать алгоритм подсчета очков и вывода их в .txt/.csv файл
 - [x] Создать элементы интерфейса
 - [x] Разработать режимы PVE и PVP
> Опционально (необязательно):
> - [ ] Реализовать воду, при наезде на которую танк топится
> - [ ] Реализовать механику режима CTF (capture the flag)
> - [x] Разработать класс `Mine` (мина, при наезде на которую у танка в зависимости от команды снимается определенное количество очков здоровья

# Презентация
https://docs.google.com/presentation/d/1kBx29MD0uOMik2gyq74IFha9ZVV6Js12w2sjnJeTusE/edit?usp=sharing
# Пояснительная записка
### Название проекта
Tanks Retro Game
### Автор проекта
Карнажицкий Максим Романович
### Идея проекта
Идея проекта заключалась в создании простого 2д платформера с возможностью сражения против ботов или игрока с добавлением различных полезных функций.
Визуальная составляющая сделана "с закосом" на Денди-стиль, но большая часть спрайтов нарисована мной (поэтому все так убого).
Стреляя в противнков и устраивая засады из кустов вы можете победить.
### Реализация
Игра сделана на ЯП python, библиотека pygame==2.1.2.
В ходе разработки я сталкивался с некоторым количеством багов, большую часть которых благополучно удалось испроваить (90% где-то).
Из интересного стоит отметить реализацию "качельной" анимации бустеров с помощью функции синусоиды и растяжения графика.

| Класс         | Унаследован от     | Назначение |
| ------------- |:---------------------:| -----:|
| ClassicTank     | pg.sprite.Sprite   | Набор характеристик танка |
| ClassicTankPlayer    | ClassicTank |   Игрок |
| ClassicTankBot | ClassicTank       |    Бот, цели для убийства которого зависят от его команды |
| ClassicBullet| pg.sprite.Sprite | Спрайт снаряда |
| BrickWall, Bush  | pg.sprite.Sprite| Разрушаемая стена, Куст 
| Booster| pg.sprite.Sprite| Спрайт бустера, который можно подобрать и получить определенный бонус к ТТХ|
| SpeedBooster, DamageBooster, ArmorBooster, HealthBooster| Booster| Сами бустеры, наследующиеся от родительского класса|
|Mine | pg.sprite.Sprite|Могут размещать танки команд|
|MapBoard | | Карта уровня в виде сетки, позволяющая создавать свои карты|
|InterfaceForClassicTank| |Класс, отвечающий за все индикаторы, вывод очков, характеристик, переключения и прочего |
| GravityParticle| GravityParticle| Частица, падающая вниз|
| FlyingParticle|pg.sprite.Sprite | Частица, исчезающая в воздухе|
| ParticleKilledTank, ParticleHitBrick| GravityParticle| Частица танка после смерти, частица нанесения урона кирпичной стене|
| ParticleHitTank| FlyingParticle| Частица попадания в танк транслирует нанесенный урон|
| ClassicBulletParticle| pg.sprite.Sprite| Частица летящего снаряда| 
| FireParticle| pg.sprite.Sprite| Частица выстрела|
