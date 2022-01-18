<?php

namespace App\Entity;

use App\Repository\CityRepository;
use Doctrine\ORM\Mapping as ORM;
use Doctrine\ORM\Mapping\JoinColumn;
use Doctrine\ORM\Mapping\ManyToOne;

/**
 * @ORM\Table(name="cities", options={"collate":"utf8mb4_unicode_ci", "charset":"utf8mb4", "engine":"InnoDB", "ROW_FORMAT":"COMPACT"})
 * @ORM\Entity(repositoryClass=CityRepository::class)
 */
class City
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue
     * @ORM\Column(type="bigint", length=8, name="id", options={"unsigned"=true})
     */
    private $id;

    /**
     * @ORM\Column(type="string", name="name", length=255, options={"collation":"utf8mb4_unicode_ci"})
     */
    private $name;

    /**
     * @ORM\Column(type="string", name="state_code", length=10, options={"collation":"utf8mb4_unicode_ci"})
     */
    private $stateCode;

    /**
     * @ORM\Column(type="string", name="country_code", length=2, options={"collation":"utf8mb4_unicode_ci"})
     */
    private $countryCode;

    /**
     * @ORM\Column(type="decimal", precision=10, scale=8, nullable=true, name="latitude", options={"default"=NULL})
     */
    private $latitude;

    /**
     * @ORM\Column(type="decimal", precision=11, scale=8, nullable=true, name="longitude", options={"default"=NULL})
     */
    private $longitude;

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

    /**
     * @ManyToOne(targetEntity="State")
     * @JoinColumn(name="state_id", referencedColumnName="id")
     */
    private $state;

    /**
     * @ManyToOne(targetEntity="Country")
     * @JoinColumn(name="country_id", referencedColumnName="id")
     */
    private $country;


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
    public function getStateCode()
    {
        return $this->stateCode;
    }

    /**
     * @param mixed $stateCode
     */
    public function setStateCode($stateCode): void
    {
        $this->stateCode = $stateCode;
    }

    /**
     * @return mixed
     */
    public function getCountryCode()
    {
        return $this->countryCode;
    }

    /**
     * @param mixed $countryCode
     */
    public function setCountryCode($countryCode): void
    {
        $this->countryCode = $countryCode;
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

    /**
     * @return mixed
     */
    public function getState()
    {
        return $this->state;
    }

    /**
     * @param mixed $state
     */
    public function setState($state): void
    {
        $this->state = $state;
    }

    /**
     * @return mixed
     */
    public function getCountry()
    {
        return $this->country;
    }

    /**
     * @param mixed $country
     */
    public function setCountry($country): void
    {
        $this->country = $country;
    }
}
