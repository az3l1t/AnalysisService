package net.az3l1t.emias.repository;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;

@Repository
@RequiredArgsConstructor
public class AnalysisResultRepository implements AnalysisRepository {
    private final RedisTemplate<String, String> redisTemplate;

    @Value("${spring.duration.saving}")
    private int duration;

    public void save(String key, String value) {
        redisTemplate.opsForValue().set(key, value, Duration.ofMinutes(duration));
    }

    public String get(String key) {
        return redisTemplate.opsForValue().get(key);
    }
}
