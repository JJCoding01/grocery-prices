select
    S.Store,
    C.Category,
    I.Description,
    P.Price
from (select
    P.ItemID,
    I.CategoryID,
    P.StoreID,
    min(P.Price) as Price

from Prices as P
    inner join Stores as S on P.StoreID = S.StoreID
    inner join Items as I on P.ItemID = I.ItemID

where
    S.Active = 1 and I.Active = 1  -- Store and item are active and should be included
    and P.PreferenceTypeID in (select TypeID from PreferenceTypes where ShortType in ("P", "S")) -- filter out any priced items that positively wanted
    and (I.PreferredStoreID is null or I.PreferredStoreID = P.StoreID)
group by P.ItemID) as P

inner join Stores as S on P.StoreID = S.StoreID
inner join Items as I on P.ItemID = I.ItemID
inner join Categories as C on P.CategoryID = C.CategoryID
