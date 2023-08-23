from mongoclasses.operators import update as upd


def test_current_date():
    assert upd.current_date({"last_modified": True}) == {
        "$currentDate": {"last_modified": True}
    }

    assert upd.current_date(last_modified=True) == {
        "$currentDate": {"last_modified": True}
    }


def test_inc():
    assert upd.inc({"quantity": -2}) == {"$inc": {"quantity": -2}}

    assert upd.inc(quantity=-2) == {"$inc": {"quantity": -2}}


def test_min():
    assert upd.min({"low_score": 150}) == {"$min": {"low_score": 150}}

    assert upd.min(low_score=150) == {"$min": {"low_score": 150}}


def test_max():
    assert upd.max({"high_score": 950}) == {"$max": {"high_score": 950}}

    assert upd.max(high_score=950) == {"$max": {"high_score": 950}}


def test_mul():
    assert upd.mul({"price": 1.25}) == {"$mul": {"price": 1.25}}

    assert upd.mul(price=1.25) == {"$mul": {"price": 1.25}}


def test_rename():
    assert upd.rename({"name.first": "name.fname"}) == {
        "$rename": {"name.first": "name.fname"}
    }

    assert upd.rename(nmae="name") == {"$rename": {"nmae": "name"}}


def test_set():
    assert upd.set(
        quantity=500,
        details={"model": "2600", "make": "Fashionaires"},
        tags=["coats", "outerwear", "clothing"],
    ) == {
        "$set": {
            "quantity": 500,
            "details": {"model": "2600", "make": "Fashionaires"},
            "tags": ["coats", "outerwear", "clothing"],
        }
    }

    assert upd.set({"details.make": "Kustom Kidz"}) == {
        "$set": {"details.make": "Kustom Kidz"}
    }


def test_set_on_insert():
    assert upd.set_on_insert({"default_qty": 100}) == {
        "$setOnInsert": {"default_qty": 100}
    }

    assert upd.set_on_insert(default_qty=100) == {"$setOnInsert": {"default_qty": 100}}


def test_unset():
    assert upd.unset({"quantity": "", "instock": ""}) == {
        "$unset": {"quantity": "", "instock": ""}
    }
    assert upd.unset(quantity="", instock="") == {
        "$unset": {"quantity": "", "instock": ""}
    }


def test_add_to_set():
    assert upd.add_to_set({"colors": "mauve"}) == {"$addToSet": {"colors": "mauve"}}
    assert upd.add_to_set(colors="mauve") == {"$addToSet": {"colors": "mauve"}}


def test_pop():
    assert upd.pop({"scores": -1}) == {"$pop": {"scores": -1}}
    assert upd.pop(scores=-1) == {"$pop": {"scores": -1}}


def test_pull():
    assert upd.pull({"vegetables": "carrots"}) == {"$pull": {"vegetables": "carrots"}}
    assert upd.pull(vegetables="carrots") == {"$pull": {"vegetables": "carrots"}}


def test_push():
    assert upd.push({"scores": 89}) == {"$push": {"scores": 89}}
    assert upd.push(scores=89) == {"$push": {"scores": 89}}


def test_pull_all():
    assert upd.pull_all({"scores": [0, 5]}) == {"$pullAll": {"scores": [0, 5]}}
    assert upd.pull_all(scores=[0, 5]) == {"$pullAll": {"scores": [0, 5]}}


def test_each():
    assert upd.each(["camera", "electronics", "accessories"]) == {
        "$each": ["camera", "electronics", "accessories"]
    }


def test_position():
    assert upd.position(0) == {"$position": 0}


def test_slice():
    assert upd.slice(-5) == {"$slice": -5}


def test_sort():
    assert upd.sort({"score": 1}) == {"$sort": {"score": 1}}


def test_bit():
    assert upd.bit({"expdata": {"and": 10}}) == {"$bit": {"expdata": {"and": 10}}}
    assert upd.bit(expdata={"and": 10}) == {"$bit": {"expdata": {"and": 10}}}
