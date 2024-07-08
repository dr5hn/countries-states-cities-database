<?php


namespace bin\Support;

use Monolog\Level;
use Monolog\Logger;
use Monolog\Handler\StreamHandler;
use Monolog\Handler\FirePHPHandler;
use Noodlehaus\Config as YamlConfig;
use mysqli;
use Exception;


class Config
{
    private static ?Config $me = null;

    private Env $env;

    /**
     * @var Logger[]
     */
    private array $logger = [];

    private ?YamlConfig $yamlConfig;

    /**
     * @return Config
     */
    public static function getConfig(): Config
    {
        if (is_null(self::$me)) {
            static::$me = new Config();
        }
        return static::$me;
    }

    public function __construct()
    {
        $this->env = new Env(PATH_BASE . '/');

        $_ENV["PHINX_DBHOST"] = $this->getSettings()->get('database.mysql.hostname');
        $_ENV["PHINX_DBNAME"] = $this->getSettings()->get('database.mysql.database');
        $_ENV["PHINX_DBUSER"] = $this->getSettings()->get('database.mysql.username');
        $_ENV["PHINX_DBPASS"] = $this->getSettings()->get('database.mysql.password');
        $_ENV["PHINX_DBPORT"] = $this->getSettings()->get('database.mysql.port');
        $_ENV["PHINX_APPENVIRONMENT"] = $this->getEnv()->get('APP_ENVIRONMENT');
        $_ENV["PHINX_PATH_MIGRATIONS"] = PATH_BASE.'/db';
    }

    /**
     * @return Env
     */
    public function getEnv(): Env
    {
        return $this->env;
    }

    /**
     * @param string $name
     * @param $level
     * @return Logger
     */
    public function getLogger(string $name = "app_logger", $level = Level::Debug): Logger
    {
        if (isset($this->logger[$name])) {
            return $this->logger[$name];
        }

        $path = $this->getConfig()->get('application.path_log');

        $stream = new StreamHandler(PATH_BASE . $path . '/' . $level . '.log', $level);
        $firephp = new FirePHPHandler();

        $logger = new Logger($name);
        $logger->pushHandler($stream);

        return $this->logger[$name] = $logger;
    }

    public function getSettings(): YamlConfig
    {
        if (!empty($this->yamlConfig)) {
            return $this->yamlConfig;
        }
        $config = new YamlConfig(PATH_BASE . '/config/app.yaml');
        $config->set('path_base', PATH_BASE);
        $config->set('env', $this->env);

        return $this->yamlConfig = $config;
    }


    public function getDB()
    {
        $conn = new mysqli(
            $this->getSettings()->get('database.mysql.hostname'),
            $this->getSettings()->get('database.mysql.username'),
            $this->getSettings()->get('database.mysql.password'),
            $this->getSettings()->get('database.mysql.database'),
            $this->getSettings()->get('database.mysql.port')
        );

        if ($conn->connect_error) {
            throw new Exception("Connection failed: " . $conn->connect_error);
        }
        if (!$conn->set_charset("utf8mb4")) {
            throw new Exception("Error loading character set utf8: %s\n", $conn->error);
        }
        return $conn;
    }


}