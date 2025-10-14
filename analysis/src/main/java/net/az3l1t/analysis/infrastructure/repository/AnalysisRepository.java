package net.az3l1t.analysis.infrastructure.repository;

import net.az3l1t.analysis.infrastructure.entity.AnalysisResultDocument;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface AnalysisRepository extends MongoRepository<AnalysisResultDocument, String> {
}
