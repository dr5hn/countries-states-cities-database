<?php

namespace bin\Support;

use Dotenv\Dotenv;
use Dotenv\Repository\RepositoryBuilder;
use Dotenv\Repository\RepositoryInterface;

class Env
{
    private RepositoryInterface $repository;
    private Dotenv $dotenv;

    /**
     * Load the environment into the repository
     *
     * @param  string|string[]  $paths
     * @param  string|string[]  $names
     */
    public function __construct(
        string|array $paths,
        string|array $names = '.env',
        ?RepositoryInterface $repository = null,
    ) {
        $this->repository = $repository ?? RepositoryBuilder::createWithDefaultAdapters()->immutable()->make();
        $this->dotenv = Dotenv::create($this->repository, $paths, $names);
        $this->dotenv->load();
    }

    /*
     * Get the value of the environment variable, returning $default if it is not defined.
     */
    public function get(string $key, $default = null): ?string
    {
        return $this->repository->get($key) ?? $default;
    }

    /*
     * Get the value of the environment variable as a boolean, returning $default if it is not defined.
     *
     * Note, that this method maps the string value of "false" (of whatever case) to the PHP boolean type false
     *
     */
    public function getBool(string $key, bool $default = false): bool
    {
        $value = $this->get($key);
        if ($value === null) {
            return $default;
        }

        if (strtolower($value) === 'false') {
            return false;
        }

        return (bool)$value;
    }
}