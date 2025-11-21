package net.az3l1t.analysis.infrastructure.adapter.out.persistence;

import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.adapter.out.persistence.mapper.PersistenceMapper;
import net.az3l1t.analysis.infrastructure.entity.AnalysisResultDocument;
import net.az3l1t.analysis.infrastructure.repository.AnalysisRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AnalysisResultMongoAdapterTest {

    @Mock
    private AnalysisRepository analysisRepository;
    @Mock
    private PersistenceMapper persistenceMapper;

    @InjectMocks
    private AnalysisResultMongoAdapter adapter;

    private AnalysisResult domainResult;
    private AnalysisResultDocument document;

    @BeforeEach
    void setUp() {
        domainResult = new AnalysisResult(null, 1L, 2L, LocalDateTime.now(), false, Map.of("hb", "12"));
        document = new AnalysisResultDocument("generated-id", 1L, 2L, domainResult.getAnalysisTime(), false, domainResult.getResults());
    }

    @Test
    void shouldSaveAndUpdateId() {
        when(persistenceMapper.toEntity(domainResult)).thenReturn(document);

        adapter.save(domainResult);

        assertThat(domainResult.getId()).isEqualTo("generated-id");
        verify(analysisRepository).save(document);
    }

    @Test
    void shouldFindByIdOptional() {
        when(analysisRepository.findById("generated-id")).thenReturn(Optional.of(document));
        when(persistenceMapper.toModel(document)).thenReturn(domainResult);

        Optional<AnalysisResult> result = adapter.findByIdOptional("generated-id");

        assertThat(result).contains(domainResult);
    }

    @Test
    void shouldThrowWhenIdNotFound() {
        when(analysisRepository.findById("missing")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> adapter.findById("missing"))
                .isInstanceOf(RuntimeException.class)
                .hasMessageContaining("missing");
    }

    @Test
    void shouldReturnPagedResults() {
        Page<AnalysisResultDocument> docs = new PageImpl<>(List.of(document));
        when(analysisRepository.findAll(PageRequest.of(0, 5))).thenReturn(docs);
        when(persistenceMapper.toModel(document)).thenReturn(domainResult);

        Page<AnalysisResult> actual = adapter.findAll(0, 5);

        assertThat(actual.getContent()).containsExactly(domainResult);
    }

    @Test
    void shouldDeleteById() {
        adapter.deleteById("generated-id");
        verify(analysisRepository).deleteById("generated-id");
    }
}

