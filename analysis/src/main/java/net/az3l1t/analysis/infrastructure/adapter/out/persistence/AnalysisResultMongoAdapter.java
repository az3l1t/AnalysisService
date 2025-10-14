package net.az3l1t.analysis.infrastructure.adapter.out.persistence;

import lombok.RequiredArgsConstructor;
import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.domain.port.out.AnalysisResultPort;
import net.az3l1t.analysis.infrastructure.adapter.out.persistence.mapper.PersistenceMapper;
import net.az3l1t.analysis.infrastructure.entity.AnalysisResultDocument;
import net.az3l1t.analysis.infrastructure.repository.AnalysisRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Component;
import java.util.Optional;

@Component
@RequiredArgsConstructor
public class AnalysisResultMongoAdapter implements AnalysisResultPort {
    private final AnalysisRepository analysisRepository;
    private final PersistenceMapper persistenceMapper;

    @Override
    public AnalysisResult save(AnalysisResult result) {
        AnalysisResultDocument document = persistenceMapper.toEntity(result);
        analysisRepository.save(document);
        result.setId(document.getId());
        return result;
    }

    @Override
    public Optional<AnalysisResult> findByIdOptional(String id) {
        return analysisRepository.findById(id)
                .map(persistenceMapper::toModel);
    }

    @Override
    public AnalysisResult findById(String id) {
        return findByIdOptional(id)
                .orElseThrow(() -> new RuntimeException("No result found with id: " + id));
    }

    @Override
    public Page<AnalysisResult> findAll(int page, int size) {
        Page<AnalysisResultDocument> docs = analysisRepository.findAll(PageRequest.of(page, size));
        return docs.map(persistenceMapper::toModel);
    }

    @Override
    public void deleteById(String id) {
        analysisRepository.deleteById(id);
    }
}
