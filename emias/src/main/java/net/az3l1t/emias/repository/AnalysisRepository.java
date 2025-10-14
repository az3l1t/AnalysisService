package net.az3l1t.emias.repository;

public interface AnalysisRepository {
    void save(String key, String value);
    String get(String key);
}
