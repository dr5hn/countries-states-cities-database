<?php

namespace App\Entity;

use App\Repository\CountryRepository;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Table(name="countries", options={"collate":"utf8mb4_unicode_ci", "charset":"utf8mb4", "engine":"InnoDB"})
 * @ORM\Entity(repositoryClass=CountryRepository::class)
 */
class Country
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue
     * @ORM\Column(type="bigint", length=8, name="id", options={"unsigned"=true})
     */
    private $id;

    /**
     * @ORM\Column(type="string", name="name", length=100, options={"collation":"utf8mb4_unicode_ci"})
     */
    private $name;

    /**
     * @ORM\Column(type="string", name="iso3", length=3, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $iso3;

    /**
     * @ORM\Column(type="string", name="numeric_code", length=3, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $numericCode;

    /**
     * @ORM\Column(type="string", name="iso2", length=2, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $iso2;

    /**
     * @ORM\Column(type="string", name="phonecode", length=255, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $phoneCode;

    /**
     * @ORM\Column(type="string", name="capital", length=255, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $capital;

    /**
     * @ORM\Column(type="string", name="currency", length=255, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $currency;

    /**
     * @ORM\Column(type="string", name="currency_name", length=255, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $currencyName;

    /**
     * @ORM\Column(type="string", name="currency_symbol", length=255, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $currencySymbol;

    /**
     * @ORM\Column(type="string", name="tld", length=255, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $tld;

    /**
     * @ORM\Column(type="string", name="native", length=255, nullable=true, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $native;

    /**
     * @ORM\Column(type="string", name="region", length=255, nullable=true, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $region;

    /**
     * @ORM\Column(type="string", name="subregion", length=255, nullable=true, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $subRegion;

    /**
     * @ORM\Column(type="text", name="timezones")
     */
    private $timezones;

    /**
     * @ORM\Column(type="text", name="translations")
     */
    private $translations;

    /**
     * @ORM\Column(type="decimal", precision=10, scale=8, name="latitude", options={"default"=NULL})
     */
    private $latitude;

    /**
     * @ORM\Column(type="decimal", precision=11, scale=8, name="longitude", options={"default"=NULL})
     */
    private $longitude;

    /**
     * @ORM\Column(type="string", name="emoji", length=191, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $emoji;

    /**
     * @ORM\Column(type="string", name="emojiU", length=191, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $emojiU;

    /**
     * @ORM\Column(type="datetime", name="created_at", options={"default"=NULL})
     */
    private $dateCreated;

    /**
     * @ORM\Column(type="datetime", name="updated_at", options={"default"=NULL})
     */
    private $dateUpdated;

    /**
     * @ORM\Column(type="boolean", name="flag", options={"default"=1})
     */
    private $flag;

    /**
     * @ORM\Column(type="string", name="wikiDataId", nullable=true, length=255, options={"default"=NULL, "collation":"utf8mb4_unicode_ci"})
     */
    private $wikiDataId;

    public function getId(): ?int
    {
        return $this->id;
    }

    /**
     * @return mixed
     */
    public function getName()
    {
        return $this->name;
    }

    /**
     * @param mixed $name
     */
    public function setName($name): void
    {
        $this->name = $name;
    }

    /**
     * @return mixed
     */
    public function getIso3()
    {
        return $this->iso3;
    }

    /**
     * @param mixed $iso3
     */
    public function setIso3($iso3): void
    {
        $this->iso3 = $iso3;
    }

    /**
     * @return mixed
     */
    public function getNumericCode()
    {
        return $this->numericCode;
    }

    /**
     * @param mixed $numericCode
     */
    public function setNumericCode($numericCode): void
    {
        $this->numericCode = $numericCode;
    }

    /**
     * @return mixed
     */
    public function getIso2()
    {
        return $this->iso2;
    }

    /**
     * @param mixed $iso2
     */
    public function setIso2($iso2): void
    {
        $this->iso2 = $iso2;
    }

    /**
     * @return mixed
     */
    public function getPhoneCode()
    {
        return $this->phoneCode;
    }

    /**
     * @param mixed $phoneCode
     */
    public function setPhoneCode($phoneCode): void
    {
        $this->phoneCode = $phoneCode;
    }

    /**
     * @return mixed
     */
    public function getCapital()
    {
        return $this->capital;
    }

    /**
     * @param mixed $capital
     */
    public function setCapital($capital): void
    {
        $this->capital = $capital;
    }

    /**
     * @return mixed
     */
    public function getCurrency()
    {
        return $this->currency;
    }

    /**
     * @param mixed $currency
     */
    public function setCurrency($currency): void
    {
        $this->currency = $currency;
    }

    /**
     * @return mixed
     */
    public function getCurrencyName()
    {
        return $this->currencyName;
    }

    /**
     * @param mixed $currencyName
     */
    public function setCurrencyName($currencyName): void
    {
        $this->currencyName = $currencyName;
    }

    /**
     * @return mixed
     */
    public function getCurrencySymbol()
    {
        return $this->currencySymbol;
    }

    /**
     * @param mixed $currencySymbol
     */
    public function setCurrencySymbol($currencySymbol): void
    {
        $this->currencySymbol = $currencySymbol;
    }

    /**
     * @return mixed
     */
    public function getTld()
    {
        return $this->tld;
    }

    /**
     * @param mixed $tld
     */
    public function setTld($tld): void
    {
        $this->tld = $tld;
    }

    /**
     * @return mixed
     */
    public function getNative()
    {
        return $this->native;
    }

    /**
     * @param mixed $native
     */
    public function setNative($native): void
    {
        $this->native = $native;
    }

    /**
     * @return mixed
     */
    public function getRegion()
    {
        return $this->region;
    }

    /**
     * @param mixed $region
     */
    public function setRegion($region): void
    {
        $this->region = $region;
    }

    /**
     * @return mixed
     */
    public function getSubRegion()
    {
        return $this->subRegion;
    }

    /**
     * @param mixed $subRegion
     */
    public function setSubRegion($subRegion): void
    {
        $this->subRegion = $subRegion;
    }

    /**
     * @return mixed
     */
    public function getTimezones()
    {
        return $this->timezones;
    }

    /**
     * @param mixed $timezones
     */
    public function setTimezones($timezones): void
    {
        $this->timezones = $timezones;
    }

    /**
     * @return mixed
     */
    public function getTranslations()
    {
        return $this->translations;
    }

    /**
     * @param mixed $translations
     */
    public function setTranslations($translations): void
    {
        $this->translations = $translations;
    }

    /**
     * @return mixed
     */
    public function getLatitude()
    {
        return $this->latitude;
    }

    /**
     * @param mixed $latitude
     */
    public function setLatitude($latitude): void
    {
        $this->latitude = $latitude;
    }

    /**
     * @return mixed
     */
    public function getLongitude()
    {
        return $this->longitude;
    }

    /**
     * @param mixed $longitude
     */
    public function setLongitude($longitude): void
    {
        $this->longitude = $longitude;
    }

    /**
     * @return mixed
     */
    public function getEmoji()
    {
        return $this->emoji;
    }

    /**
     * @param mixed $emoji
     */
    public function setEmoji($emoji): void
    {
        $this->emoji = $emoji;
    }

    /**
     * @return mixed
     */
    public function getEmojiU()
    {
        return $this->emojiU;
    }

    /**
     * @param mixed $emojiU
     */
    public function setEmojiU($emojiU): void
    {
        $this->emojiU = $emojiU;
    }

    /**
     * @return mixed
     */
    public function getDateCreated()
    {
        return $this->dateCreated;
    }

    /**
     * @param mixed $dateCreated
     */
    public function setDateCreated($dateCreated): void
    {
        $this->dateCreated = $dateCreated;
    }

    /**
     * @return mixed
     */
    public function getDateUpdated()
    {
        return $this->dateUpdated;
    }

    /**
     * @param mixed $dateUpdated
     */
    public function setDateUpdated($dateUpdated): void
    {
        $this->dateUpdated = $dateUpdated;
    }

    /**
     * @return mixed
     */
    public function getFlag()
    {
        return $this->flag;
    }

    /**
     * @param mixed $flag
     */
    public function setFlag($flag): void
    {
        $this->flag = $flag;
    }

    /**
     * @return mixed
     */
    public function getWikiDataId()
    {
        return $this->wikiDataId;
    }

    /**
     * @param mixed $wikiDataId
     */
    public function setWikiDataId($wikiDataId): void
    {
        $this->wikiDataId = $wikiDataId;
    }
}
